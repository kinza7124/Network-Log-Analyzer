# Network Security SOC Dashboard

A comprehensive Network Security Operations Center (SOC) dashboard that combines real-time attack detection, visualizations, ChatOps, and automated email escalation.

## Features

- 🛡️ **Real-time Attack Detection**: Uses trained GHF-ART model to detect network attacks
- 📊 **Interactive Visualizations**: Charts and graphs for attack analysis
- 💬 **ChatOps Integration**: AI-powered chatbot for security analysis
- 📧 **Email Escalation**: Automated email alerts to network administrators
- 🔴 **Live Alert Feed**: Real-time monitoring and alerting system

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
3. **💬 ChatOps**: AI assistant for security queries
4. **⚙️ Settings**: System configuration and status

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

## License

This project is for educational and research purposes.

## Support

For issues or questions, please check:
1. All dependencies are installed
2. Model is trained (`ghf_art_model.pkl` exists)
3. Data file exists (`network_logs_processed.csv`)
4. `.env` file is configured correctly

