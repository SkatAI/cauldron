Here is your implementation plan aimed at a single-server, persistent-storage setup:

### 1. The Setup
*   **Storage:** Persistent database (SQL/NoSQL) storing a timestamp for every request made via the **Free Tier**.
*   **Keys:** Load both `FREE_API_KEY` and `PAID_API_KEY` in environment variables.

### 2. The Logic (Before Request)
Before sending a request, query your storage:
1.  **Check Minute:** Count records where `timestamp > (Now - 60 seconds)`.
    *   *Threshold:* **13** (buffer for latency/synchronization).
2.  **Check Day:** Count records where `timestamp > (Start of Day)`.
    *   *Threshold:* **1,450** (buffer against the 1,500 limit).

**Decision:**
*   If **both** counts are below thresholds → **Use Free Key**.
*   If **either** count exceeds threshold → **Use Paid Key**.

### 3. The Safety Net (During Request)
Wrap the **Free Key** call in a `try/catch` block.
*   If the Free Key returns `429 Resource Exhausted` (despite your checks), catch the error and immediately retry with the **Paid Key**.
*   *Why:* This handles edge cases where Google's server-side counter slightly disagrees with your local database.

### 4. Post-Request
*   If the request was sent using the **Free Key** (and succeeded), save the current timestamp to your database to update the "sliding window" for the next call.