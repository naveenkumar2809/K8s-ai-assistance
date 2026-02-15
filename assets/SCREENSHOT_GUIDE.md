# Screenshot Capture Guide for K8s Pilot

This guide will help you capture professional screenshots of your K8s Pilot application for the README.

## Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- Browser (Chrome/Edge recommended for best DevTools)

## Recommended Tools
- **Windows**: Snipping Tool (Win + Shift + S) or ShareX (free)
- **Browser Extension**: Awesome Screenshot, Nimbus Screenshot
- **For GIFs**: ScreenToGif (Windows), LICEcap (cross-platform)

## Screenshots to Capture

### 1. Dashboard Overview (`dashboard.png`)
**URL**: `http://localhost:3000/`

**What to capture**:
- Full dashboard view showing:
  - Cluster Health cards (Nodes, Active Pods, Unhealthy)
  - Real-time CPU Usage chart
  - Recent Events section
  - AI Recommendations panel (if any are active)

**Tips**:
- Wait for WebSocket to connect (green "Connected" badge)
- Let the CPU chart populate with some data points
- Zoom browser to 90% for better overview (Ctrl + Mouse Wheel)

**Recommended size**: 1600x900px or 1920x1080px

---

### 2. AI Chat Interface (`ai-chat.png`)
**URL**: `http://localhost:3000/chat`

**What to capture**:
- Chat interface showing a conversation
- Example questions to ask before screenshot:
  1. "How is the cluster health?"
  2. "Are there any recommendations?"
  3. "Show me recent errors"

**Tips**:
- Capture after asking 2-3 questions to show conversation flow
- Include both user messages (blue) and bot responses (purple)
- Show the input field at the bottom

**Recommended size**: 1200x800px

---

### 3. Recommendations Flow (`recommendations.png`)
**URL**: `http://localhost:3000/`

**What to capture**:
- Focus on the right sidebar showing AI Recommendations
- If no recommendations appear naturally, you can trigger them by:
  - Creating high CPU load on a pod
  - Or wait for the mock anomaly detection to generate some

**Tips**:
- Capture showing at least 1-2 recommendation cards
- Include the "Apply" and "Discard" buttons
- Show the severity indicators (red/yellow borders)

**Recommended size**: 800x600px (cropped to recommendations panel)

---

### 4. Resource Explorer (`resource-explorer.png`)
**URLs**: 
- Nodes: `http://localhost:3000/nodes`
- Pods: `http://localhost:3000/pods`

**Option A - Combined Screenshot**:
- Capture Nodes page, then Pods page
- Use image editor to combine them vertically

**Option B - Separate Screenshots**:
- Create `nodes.png` and `pods.png` separately

**Tips**:
- Show the full table with all columns visible
- Ensure status badges are visible (green "Ready", "Running")
- Capture the header with page title

**Recommended size**: 1400x700px each

---

## Creating GIFs (Optional but Impressive)

### Dashboard Animation (`dashboard.gif`)
**What to show**:
1. Page loads
2. WebSocket connects
3. CPU chart updates in real-time
4. Events stream in
5. (Optional) A recommendation appears

**Duration**: 5-10 seconds
**Tool**: ScreenToGif or LICEcap
**Size**: Keep under 5MB for GitHub

### Chat Interaction (`chat-interaction.gif`)
**What to show**:
1. User types a question
2. Sends it
3. Bot "thinking" animation (three dots)
4. Response appears

**Duration**: 5-8 seconds

---

## Post-Processing Tips

1. **Crop**: Remove browser chrome (address bar, bookmarks) for cleaner look
2. **Resize**: Optimize for web (max width 1920px)
3. **Compress**: Use TinyPNG or similar to reduce file size
4. **Format**: PNG for screenshots, GIF or WebP for animations

---

## File Naming Convention

Save files in the `assets/` folder with these exact names:
- `dashboard.png` - Main dashboard view
- `ai-chat.png` - Chat interface
- `recommendations.png` - Recommendations panel
- `resource-explorer.png` - Nodes/Pods tables
- `dashboard.gif` (optional) - Animated dashboard
- `chat-interaction.gif` (optional) - Animated chat

---

## After Capturing

1. Save all images to `c:/Nvn/myAI/k8s-ai-assistant/assets/`
2. Open `README.md`
3. Uncomment the image lines (remove `<!--` and `-->`)
4. Commit to Git:
   ```bash
   git add assets/
   git add README.md
   git commit -m "Add application screenshots"
   ```

---

## Quick Capture Checklist

- [ ] Dashboard screenshot (main view)
- [ ] AI Chat screenshot (with conversation)
- [ ] Recommendations screenshot (showing cards)
- [ ] Resource Explorer screenshot (nodes/pods)
- [ ] (Optional) Dashboard GIF
- [ ] (Optional) Chat interaction GIF
- [ ] Uncomment image references in README.md
- [ ] Verify images display correctly in README
