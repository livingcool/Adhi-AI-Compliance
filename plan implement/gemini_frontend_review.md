node.exe : Loaded cached credentials.
At C:\Users\Admin\AppData\Roaming\npm\gemini.ps1:22 char:14
+ ...    $input | & "node$exe"  "$basedir/node_modules/@google/gemini-cli/d ...
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (Loaded cached credentials.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
Hook registry initialized with 0 hook entries
As a senior frontend engineer, I have conducted a thorough review of the 'Adhi Compliance' Next.js codebase. Below is my structured report detailing critical issues, areas for improvement, and a prioritized action plan.

***

## Frontend Code Review: Adhi Compliance Platform

### 1. CRITICAL ISSUES (Blocking Bugs)

These issues will prevent the application from building or running correctly and must be addressed immediately.

*   **Broken Imports:** Almost every file contains import paths with a leading space (e.g., `import ... from " @/lib/api"`). This is a syntax error and will cause module resolution to fail across the entire application.
    *   **Files Affected:** Nearly all `.ts` and `.tsx` files.
    *   **Suggestion:** Perform a project-wide search and replace for `from " @/` and change it to `from "@/`.

*   **API Proxy Misconfiguration:** The `rewrites` rule in `webapp/next.config.ts` is configured incorrectly. It proxies requests from `/api/:path*` to `http://127.0.0.1:8000/api/v1/:path*`. When the frontend calls an endpoint like `/api/v1/query`, the `:path*` becomes `v1/query`, resulting in a duplicated path: `.../api/v1/v1/query`.
    *   **File:** `webapp/next.config.ts`
    *   **Suggestion:** Change the destination to `http://127.0.0.1:8000/:path*`. This will correctly map `/api/v1/query` to `http://127.0.0.1:8000/v1/query`.

    ```typescript
    // webapp/next.config.ts
    const nextConfig: NextConfig = {
      // ...
      async rewrites() {
        return [
          {
            source: "/api/:path*",
            // FIX: Remove the hardcoded /api/v1 from the destination
            destination: "http://127.0.0.1:8000/:path*",
          },
        ];
      },
    };
    ```

*   **Missing Dependency:** The file `webapp/app/api/identity/analyze/route.ts` imports the `cheerio` package, but a comment explicitly states it needs to be installed. Without this dependency in `package.json`, the build will fail.

*   **Invalid Component Prop Type:** The dynamic route page `webapp/app/systems/[id]/page.tsx` incorrectly types the `params` prop as a `Promise`. This will cause a runtime error.
    *   **File:** `webapp/app/systems/[id]/page.tsx`
    *   **Suggestion:** The `params` object is passed directly to page components. The type should be `{ params: { id: string } }` and the `await` should be removed.

### 2. UX/UI IMPROVEMENTS

*   **Inconsistent Loading & Error States:** The application lacks a standardized approach. `chat/page.tsx` shows a nice loading bubble, while other pages use `setTimeout` or have no feedback at all. A consistent set of skeleton loaders and user-friendly error messages (e.g., a "Could not fetch data" toast) should be implemented.
*   **Inconsistent Styling:** The `settings/page.tsx` page deviates significantly from the established design system. It uses hardcoded `rgb()` colors instead of the CSS variables defined in `globals.css`, creating a jarring user experience.
*   **Poorly Accessible Modals:** The modal and drawer in `incidents/page.tsx` are not accessible. They lack focus trapping (users can tab to elements behind the modal), keyboard shortcuts (`Escape` to close), and proper ARIA roles (`dialog`, `aria-modal`).

### 3. CODE QUALITY

*   **Widespread Mock Data Duplication:** Nearly every page component defines its own large, hardcoded mock data arrays (e.g., `MOCK_SYSTEMS` in `systems/page.tsx`, `MOCK_INCIDENTS` in `incidents/page.tsx`). A `lib/mock-data.ts` file exists but is largely ignored. This duplication makes the codebase difficult to maintain and transition to a real API.
*   **Unused & Inconsistent API Layer:** The file `lib/api.ts` defines a comprehensive set of typed API functions, but these are almost entirely unused in favor of mock data. This points to a disconnected or abandoned refactoring effort.
*   **Component Underutilization:** A reusable `GlassCard.tsx` component exists but is not used. Instead, its styles (`glass-card` class) are applied directly in JSX, defeating the purpose of component-driven development.
*   **Invalid CSS:** The `@theme inline` directive in `globals.css` is not standard CSS and should be investigated or removed.
*   **Minor Bug:** In `webapp/app/bias/page.tsx`, the `MetricBar` component renders literal `???` placeholders for thresholds instead of the correct `<` or `>` operators.

### 4. PERFORMANCE

*   **No Code Splitting for Heavy Components:** Components that are heavy or not immediately needed, such as `ManagerConsole.tsx` (using `framer-motion`) or the `recharts`-based `VisualizationDisplay.tsx`, should be lazy-loaded with `next/dynamic`. This will significantly improve initial page load times.
*   **No Image Optimization:** The application does not use the `<Image>` component from `next/image`. All images should be served through it to get automatic optimization, resizing, and modern format conversion (WebP).
*   **Lack of Memoization:** Many components rendered in lists (e.g., `MetricBar`, `SystemCard`) are not wrapped in `React.memo`. This causes them to re-render unnecessarily when their parent component's state changes, leading to performance degradation.

### 5. SECURITY

*   **Potential XSS Vulnerability in Chat:** In `chat/page.tsx`, AI responses are parsed for bold text (`**...**`) and rendered using a `<strong>` tag. This is unsafe. If the AI output can be manipulated, it could inject malicious HTML.
    *   **Suggestion:** Use a dedicated, sanitizing Markdown library like `DOMPurify` to render AI responses safely.
*   **Improper Environment Variable Handling:**
    1.  **Server-side variables are marked as public:** `NEXT_PUBLIC_APP_BACKEND_URL` is used in a server-side route handler. The `NEXT_PUBLIC_` prefix should be reserved for variables needed by the browser.
    2.  **Unsafe non-null assertions:** `lib/supabase.ts` uses `!` (e.g., `process.env.NEXT_PUBLIC_SUPABASE_URL!`) to assert that environment variables exist. If they are missing, the app will crash. The code should validate their presence at startup and provide a clear error.

### 6. DESIGN SYSTEM

*   **Inconsistent Implementation:** As mentioned, `settings/page.tsx` completely ignores the design system.
*   **Component Neglect:** The `GlassCard.tsx` component should be the single source of truth for card styling, but it's unused.
*   **Inconsistent Naming:** The theme file is `globals.css` but contains many application-specific styles. These should be moved to component styles or a more structured CSS system (like CSS Modules).

### 7. ACCESSIBILITY

*   **Color Contrast:** Badges like `RiskBadge` and `statusBadge` use colored text on a light, colored background (e.g., `text-green-400` on `bg-green-500/15`). These combinations must be verified against WCAG AA contrast ratio requirements.
*   **Missing ARIA Labels:** Icon-only buttons (e.g., close buttons, the `ManagerConsole` trigger) lack `aria-label` attributes, making them unintelligible to screen reader users.
*   **Keyboard Navigation:** Custom form elements, like the filters, must be fully keyboard navigable.

### 8. API INTEGRATION

*   **Inconsistent Strategies:** The app is split between two API patterns: Next.js route handlers acting as a BFF (Backend-for-Frontend), and direct proxying to a backend via `next.config.ts`. A single, unified strategy should be chosen and implemented consistently.
*   **No Data Fetching Library:** The project lacks a modern data-fetching library like **SWR** or **React Query**. Using one would centralize data fetching logic and provide caching, revalidation, and request deduplication out of the box, drastically improving both performance and developer experience.
*   **No Optimistic Updates:** UI actions (like sending a chat message) wait for the API response before updating. This feels slow. Optimistic updates should be used to make the UI feel instantaneous.

### 9. MISSING FEATURES

*   **Backend Integration:** The most significant missing piece. The vast majority of the application is a mock-data-driven facade.
*   **Authentication & Authorization:** There is no user management, login, or access control.
*   **Real File Uploads:** The knowledge base upload is a mock; it does not persist the file.
*   **Responsiveness:** The application appears to be designed for desktop only and will not be usable on mobile or tablet devices without significant work on responsive layouts.

### 10. PRIORITY ACTION ITEMS

This is the recommended order of operations to stabilize and improve the codebase.

1.  **Fix Critical Build/Runtime Errors:**
    *   **Action:** Correct all broken import paths (remove the space in ` " @/.../"`).
    *   **Action:** Fix the `next.config.ts` rewrite rule.
    *   **Action:** Add `cheerio` to `package.json` or remove the unused import.
    *   **Action:** Correct the `params` prop typing in `webapp/app/systems/[id]/page.tsx`.

2.  **Unify Backend & Data Strategy:**
    *   **Action:** Replace all mock data with API calls.
    *   **Action:** Integrate **SWR** or **React Query** to manage data fetching, caching, and state.
    *   **Action:** Choose a single API communication pattern (BFF or direct proxy) and refactor to use it everywhere.

3.  **Address Security Vulnerabilities:**
    *   **Action:** Replace the unsafe string manipulation in `chat/page.tsx` with a sanitized Markdown renderer.
    *   **Action:** Correct the usage of environment variables (remove unnecessary `NEXT_PUBLIC_` prefixes and add startup validation).

4.  **Enforce the Design System:**
    *   **Action:** Refactor `settings/page.tsx` to use the application's established CSS variables and Tailwind classes.
    *   **Action:** Replace all instances of the `.glass-card` class with the `GlassCard.tsx` component.

5.  **Implement Foundational Accessibility:**
    *   **Action:** Make all modals and drawers accessible (focus trapping, keyboard controls, ARIA attributes).
    *   **Action:** Add `aria-label`s to all icon-only buttons.
    *   **Action:** Audit and fix color contrast ratios for all text.
