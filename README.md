<p align="center">
  <img src="assets/logo.svg" alt="Network Log Analyzer logo" width="120">
</p>

<h1 align="center">Network Security SOC Dashboard</h1>

<p align="center">
  Real-time network attack detection, visual analytics, ChatOps and automated email escalation
</p>

A comprehensive Network Security Operations Center (SOC) dashboard that combines real-time attack detection, visualizations, ChatOps, and automated email escalation.

## Features

- 🛡️ **Real-time Attack Detection**: Uses trained GHF-ART model to detect network attacks
- 📊 **Interactive Visualizations**: Charts and graphs for attack analysis
- 💬 **ChatOps Integration**: AI-powered chatbot for security analysis
- 📧 **Email Escalation**: Automated email alerts to network administrators
- 🔴 **Live Alert Feed**: Real-time monitoring and alerting system
- 🌓 **Dark, Light & Auto Themes**: Clean, consistent UI with a theme switcher in the sidebar

## Prerequisites

- Python 3.8+
- Trained GHF-ART model (`ghf_art_model.pkl`)
- Network logs data (`network_logs_processed.csv`)

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Train the model (if not already done):**
   ```bash
   python train_model.py
   ```

3. **Configure environment variables:**
   - Copy `env_template.txt` to `.env`
   - Fill in your email credentials and API keys

   ```bash
   cp env_template.txt .env
   ```

   Edit `.env` with your credentials:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   ADMIN_EMAIL=admin@example.com
   EMAIL_ENABLED=true
   ANTHROPIC_API_KEY=your_key_here
   ```

## Usage

### Start the Dashboard

```bash
streamlit run network_security_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Dashboard Tabs

1. **📊 Dashboard**: Visual analytics and statistics
2. **🔴 Live Alerts**: Real-time attack detection and alerts
3. **🧪 Test Data**: Upload a CSV, enter traffic manually, or simulate traffic to test the model
4. **💬 ChatOps**: AI assistant for security queries
5. **⚙️ Settings**: System configuration and status

### Themes & UI

Pick a theme from the **Theme** selector at the top of the sidebar:

| Option | Behaviour |
|--------|-----------|
| **Dark Mode** | Dark palette with a blue accent (default) |
| **Light Mode** | Light palette with a blue accent |
| **Auto** | Follows your operating system / browser light or dark setting |

The whole interface follows the selected theme: Streamlit widgets (inputs, dropdowns, tables, tabs, buttons), the custom cards, and all Plotly charts.

**UI overview:**
- **Header card** with the dashboard title and a blue accent bar
- **Metric cards** of equal height with uppercase labels for alert counts and dataset statistics
- **Underline tabs** for switching between sections
- **Filled blue buttons** for the main actions (Analyze, Send) and outlined buttons for secondary actions
- **Chart cards**: every chart sits on a bordered card and uses colours suited to the active theme
- **Severity strip** at the top of each alert (red = critical, orange = high, yellow = medium, blue = low)
- **Chat bubbles** in ChatOps that tell your messages apart from the assistant's
- **Status colours**: green for enabled/active, red for disabled/paused (email alerts, monitoring status)

**Logo:** the app's logo shows what the project does:

| Element | Meaning |
|---------|---------|
| 🛡️ Shield | Network security, the SOC's job |
| Horizontal lines | Network log entries, the data the app analyzes |
| Pulse waveform | Live traffic being analyzed in real time |
| Red point on the spike | An anomaly flagged by the GHF-ART model |

It appears as the browser tab icon, in the sidebar (as a full wordmark that collapses to the shield icon) and in the dashboard header. Logo files live in `assets/`: `logo.svg` is the icon, and `logo-wordmark-light.svg` / `logo-wordmark-dark.svg` are the wordmarks for light and dark backgrounds.

**Customising the look:** all colours are defined once in `THEME_TOKENS` near the top of `network_security_dashboard.py`, with a `dark` and a `light` palette. They drive both Streamlit's native theme and the custom CSS in `BASE_CSS`, so you can change one value (for example `primary`) and it updates everywhere.

> **Note:** The theme is applied through Streamlit's server-wide config, so it suits a dashboard run by one person locally. If several people open the same running instance and choose different themes, the native widgets follow whoever switched last. Auto mode needs Streamlit 1.46 or newer; the dashboard was tested with Streamlit 1.57.

### Real-time Monitoring

1. Enable monitoring from the sidebar
2. Click "Analyze New Traffic Sample" to test detection
3. Critical/high severity attacks trigger email alerts (if enabled)

### ChatOps

The ChatOps assistant provides intelligent security analysis using rule-based AI (no external API required). It analyzes network logs and provides insights about security threats.

**Supported Queries:**

**General Analysis:**
- "Give me a security status summary"
- "What's the overall threat level?"
- "Show me the security overview"

**Threat Investigation:**
- "Show critical alerts"
- "Show me critical alerts"
- "What attack patterns were detected?"
- "Analyze recent suspicious activity"
- "Show high severity threats"

**Time-Based Queries:**
- "What happened in the last 2 hours?"
- "Show me today's security events"
- "Recent activity in the last 6 hours"
- "Activity in the last 24 hours"

**Specific Analysis:**
- "Which services are most targeted?"
- "Analyze protocol distribution"
- "Show attack patterns"
- "What protocols are being attacked?"

**Quick Actions:**
The ChatOps tab includes quick action buttons for common queries:
- **Security Summary**: Get overall security status
- **Critical Alerts**: View high-severity threats
- **Attack Patterns**: Analyze detected attack vectors
- **Clear Chat**: Reset conversation history

**Note:** The ChatOps assistant automatically cleans HTML content from responses to ensure proper display. All responses are formatted as markdown for better readability.

## File Structure

```
CN_Proj/
├── assets/                        # Logo files (icon + light/dark wordmarks)
├── network_security_dashboard.py  # Main unified dashboard
├── train_model.py                  # Model training script
├── requirements.txt                # Python dependencies
├── env_template.txt               # Environment variables template
├── README.md                       # Project documentation
├── start_dashboard.bat            # Windows launcher script
├── start_dashboard.sh             # Linux/Mac launcher script
├── ghf_art_model.pkl             # Trained model (generated)
├── network_logs_processed.csv    # Processed network data (generated)
├── attack_alerts.json             # Alert log (generated)
└── kddcup.data_10_percent_corrected  # Training dataset
```

## Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication
2. Generate an App Password:
   - Go to Google Account → Security → 2-Step Verification
   - Generate App Password for "Mail"
3. Use the app password in `.env` as `SENDER_PASSWORD`

### Other SMTP Servers

Update `SMTP_SERVER` and `SMTP_PORT` in `.env`:
- Outlook: `smtp-mail.outlook.com:587`
- Yahoo: `smtp.mail.yahoo.com:587`
- Custom: Check your email provider's SMTP settings

## Model Training

The GHF-ART model is trained on the KDD Cup 1999 dataset:

```bash
python train_model.py
```

This generates:
- `ghf_art_model.pkl`: Trained model
- `network_logs_processed.csv`: Processed network data with predictions

## Troubleshooting

### Model Not Found
- Run `python train_model.py` first
- Ensure `ghf_art_model.pkl` exists in the project directory

### Email Not Sending
- Check `.env` file exists and has correct credentials
- Verify `EMAIL_ENABLED=true`
- Check SMTP server settings
- For Gmail, ensure App Password is used (not regular password)

### ChatOps Not Working
- Ensure `network_logs_processed.csv` exists
- Run `train_model.py` to generate the data file
- The ChatOps assistant uses rule-based AI (no API key required)
- If you see HTML tags in responses, refresh the page - responses are automatically cleaned

### HTML Content in ChatOps Responses
- The dashboard automatically removes HTML tags from ChatOps responses
- All responses are displayed as clean markdown text
- If HTML appears, it's automatically stripped before display

### Charts Show `KeyError: 'Anomaly'`
- Your Plotly version is too old for pandas 3.x (Plotly 5.x charts that group by a column crash)
- Upgrade: `pip install -r requirements.txt` (requires `plotly>=6.0.0`)

### Chatbot Warning: `'charmap' codec can't encode character`
- Caused by the Windows console being unable to print emoji in log messages
- Fixed in the dashboard, which now switches console output to UTF-8; pull the latest code if you still see it

### Theme Looks Wrong or Mixed
- Switch the theme once in the sidebar so Streamlit re-applies it, or refresh the page
- In **Auto** mode the theme follows your OS setting; change it there to switch between light and dark
- Make sure Streamlit is up to date: `pip install -U streamlit`

### Dashboard Not Loading
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Streamlit is installed: `pip install streamlit`
- Verify Python version: `python --version` (should be 3.8+)

## Development

### Adding New Features

1. **New Visualizations**: Add to Dashboard tab in `network_security_dashboard.py`
2. **New Alert Types**: Modify `detect_attack()` function
3. **ChatOps Commands**: Extend `claude_chatbot.py`

### Testing

Test individual components:
```bash
# Test model training
python train_model.py

# Test dashboard (includes all features: monitoring, ChatOps, visualizations)
streamlit run network_security_dashboard.py

```

## Next Steps

Planned extensions: live packet capture (PCAP) analysis, and turning ChatOps into a tool-using AI agent.

### 1. PCAP File Analysis

- Add `.pcap` upload to the **Test Data** tab
- Convert packets into flows (one record per connection) with [NFStream](https://www.nfstream.org/)
- Map each flow to the model's features, run detection and raise alerts as usual

### 2. Live Packet Capture

- Background worker that captures from a network interface (NFStream live mode; Npcap and admin rights needed on Windows)
- Store flows and alerts in SQLite instead of `attack_alerts.json`, so the dashboard and ChatOps share one data source
- Auto-refresh only the alert panels with `st.fragment(run_every=...)` instead of rerunning the whole page
- Only capture on networks you own or are authorised to monitor

### 3. Agent-Based ChatOps

- Migrate `claude_chatbot.py` from raw `aiohttp` requests to the official `anthropic` Python SDK, using its Tool Runner (`@beta_tool` + `client.beta.messages.tool_runner`) on a current Claude model
- Give the assistant tools such as `query_alerts(severity, since)`, `top_talkers(window)`, `get_flow(flow_id)`, `summarize_pcap(file)`, `lookup_host(ip)` and `draft_escalation(alert_ids)`
- Send the model summaries and aggregates, not raw packets (cheaper and more accurate)
- Treat packet and log contents as untrusted data, since attackers can embed instructions in payloads
- Keep a human in the loop: the agent drafts escalation emails and block recommendations, and a person confirms before anything is sent or changed

### 4. Retrain on a Modern Flow Dataset

- The current model is trained on KDD Cup 99 (1998 traffic). Only about half of its 41 features (duration, protocol, service, flags, byte counts, connection-window statistics) can be computed from live packet headers; content features such as `num_failed_logins` or `root_shell` need payload inspection and are unavailable for encrypted traffic
- Retrain on a flow-based dataset such as CIC-IDS2017 or UNSW-NB15, whose features match NFStream / CICFlowMeter output, so live traffic and training data line up
- Keep the KDD model for the existing dataset view

## Research Directions

The Next Steps above build the system; these are research questions it can be used to answer.

### 1. Online Intrusion Detection with an Incremental Model

GHF-ART is an Adaptive Resonance Theory model: it can learn from new data without retraining from scratch and without forgetting what it already learned, whereas most intrusion detection models are trained once and then frozen.

- **Question:** Does incremental ART keep detecting well on live traffic as it changes over time, compared with retraining batch models?
- **Measure:** F1 and false-positive rate over time, detection delay, throughput (flows per second)

### 2. LLM Agent for SOC Alert Triage

- **Question:** Does a tool-using agent give more accurate triage answers than a plain chatbot or the current rule-based assistant?
- **Measure:** Factual accuracy against ground truth, hallucination rate, time to triage
- **Extension:** Robustness to prompt injection hidden in packet payloads

### 3. Cross-Dataset Generalization

- **Question:** Does a model trained on CIC-IDS2017 still work on UNSW-NB15 or on locally captured traffic?
- A careful negative result is still valuable, since many published intrusion detection results do not hold across datasets

### Evaluation Checklist

- **Baselines:** Isolation Forest, autoencoder, supervised Random Forest, Kitsune (online network intrusion detector)
- **Metrics:** Precision, recall, F1, false-positive rate, PR-AUC; latency and throughput for the live system
- **Splits:** Time-based train/test splits, so the model never trains on traffic from after the traffic it is tested on
- **Ablations:** Remove one component at a time (e.g. the agent with and without tools) to show what each part contributes
- **Reproducibility:** Public datasets for the main results, fixed random seeds, released code
- **Datasets:** Use modern datasets (CIC-IDS2017, UNSW-NB15) for headline results; KDD Cup 99 is widely criticized in the literature (the reason NSL-KDD was created)

### Before Reporting Results

The dashboard currently flags 96.2% of records as anomalies with an average anomaly score of 1.000, which suggests the scores barely separate normal traffic from attacks. KDD's 10% subset is mostly attacks, so a high rate is expected, but verify the score calculation and threshold before reporting any numbers.

## License

This project is for educational and research purposes.

## Support

For issues or questions, please check:
1. All dependencies are installed
2. Model is trained (`ghf_art_model.pkl` exists)
3. Data file exists (`network_logs_processed.csv`)
4. `.env` file is configured correctly

