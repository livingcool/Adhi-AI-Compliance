"""
Test Script for Audio Pipeline Only

This script tests the complete audio ingestion pipeline:
1. Upload audio file via API
2. Monitor task progress
3. Verify database storage
4. Test retrieval

Usage:
    python test_audio_pipeline.py path/to/audio.mp3
"""

import sys
import time
import requests
from pathlib import Path

API_BASE = "http://127.0.0.1:8000/api/v1"

def test_audio_upload(audio_file_path):
    """Upload audio file and return task_id"""
    print(f"\n📤 Uploading audio file: {audio_file_path}")
    
    with open(audio_file_path, 'rb') as f:
        files = {'file': (Path(audio_file_path).name, f, 'audio/mpeg')}
        data = {
            'type': 'audio',  # MUST be 'audio' not 'pdf'!
            'source_id': Path(audio_file_path).stem
        }
        
        response = requests.post(f"{API_BASE}/ingest", files=files, data=data)
    
    if response.status_code == 202:
        task_data = response.json()
        task_id = task_data['task_id']
        print(f"✅ Upload successful! Task ID: {task_id}")
        return task_id
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def monitor_task(task_id, max_wait=600):
    """Monitor task progress until completion or failure"""
    print(f"\n⏳ Monitoring task {task_id}...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        response = requests.get(f"{API_BASE}/status/{task_id}")
        
        if response.status_code == 200:
            status_data = response.json()
            status = status_data['status']
            progress = status_data.get('progress_percent', 0)
            details = status_data.get('details', '')
            
            print(f"  Status: {status} | Progress: {progress:.1f}% | {details}")
            
            if status == 'SUCCESS':
                print(f"\n✅ Task completed successfully!")
                return True
            elif status == 'FAILURE':
                error = status_data.get('error', 'Unknown error')
                print(f"\n❌ Task failed: {error}")
                return False
        
        time.sleep(2)
    
    print(f"\n⏰ Task timeout after {max_wait}s")
    return False

def test_retrieval(query="What was discussed?"):
    """Test retrieval with audio-only filter"""
    print(f"\n🔍 Testing retrieval with query: '{query}'")
    
    payload = {
        "query": query,
        "top_k": 3,
        "filters": {"doc_type": "audio"}  # Search audio only
    }
    
    response = requests.post(f"{API_BASE}/query", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        answer = result['answer']
        sources = result['sources']
        
        print(f"\n💬 Answer: {answer}\n")
        print(f"📚 Found {len(sources)} source chunks:")
        for i, source in enumerate(sources, 1):
            print(f"\n  [{i}] Score: {source['score']:.3f}")
            print(f"      Time: {source['start_time']:.1f}s - {source['end_time']:.1f}s")
            print(f"      Text: {source['chunk_text'][:100]}...")
        
        return True
    else:
        print(f"❌ Query failed: {response.text}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_audio_pipeline.py <audio_file.mp3>")
        print("\nExample:")
        print("  python test_audio_pipeline.py test_audio.mp3")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not Path(audio_file).exists():
        print(f"❌ File not found: {audio_file}")
        sys.exit(1)
    
    # Check file size
    file_size_mb = Path(audio_file).stat().st_size / (1024 * 1024)
    print(f"📁 File size: {file_size_mb:.2f} MB")
    
    if file_size_mb > 500:
        print(f"❌ File too large! Maximum is 500MB")
        sys.exit(1)
    
    # Step 1: Upload
    task_id = test_audio_upload(audio_file)
    if not task_id:
        sys.exit(1)
    
    # Step 2: Monitor
    success = monitor_task(task_id)
    if not success:
        sys.exit(1)
    
    # Step 3: Test retrieval
    print("\n" + "="*60)
    test_retrieval()
    
    print("\n✅ Audio pipeline test complete!")

if __name__ == "__main__":
    main()
