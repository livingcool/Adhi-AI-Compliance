const fs = require('fs');
const { Client } = require('pg');

const client = new Client({
    connectionString: 'postgresql://postgres:G22a05n%4003@adhi-compliance-db.chq0mqkqaozv.ap-south-2.rds.amazonaws.com:5432/postgres'
});

async function run() {
    try {
        console.log("Connecting to database...");
        await client.connect();
        console.log("Reading SQL file...");
        const sql = fs.readFileSync('e:\\RootedAI\\SAAS\\Adhi-AI-Compliance\\ADHI-SQL-SCRATCH\\10_insert_sample_data.sql', 'utf8');
        console.log("Executing SQL...");
        await client.query(sql);
        console.log("Success! Data populated.");
    } catch (err) {
        console.error("Error executing script:", err);
    } finally {
        await client.end();
    }
}

run();
