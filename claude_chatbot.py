"""
Network Security Chatbot with Claude API Integration
Uses Anthropic's Claude API for intelligent analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os


class ClaudeSecurityChatbot:
    """
    Advanced network security chatbot with Claude API integration
    """
    
    def __init__(self, data_path="network_logs_processed.csv", api_key=None):
        """
        Initialize the chatbot
        
        Args:
            data_path: Path to network logs CSV
            api_key: Anthropic API key (optional, can use environment variable)
        """
        self.data_path = data_path
        self.df = None
        self.conversation_history = []
        
        # API configuration
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"
        
        self.load_data()
    
    def load_data(self):
        """Load network security data"""
        try:
            self.df = pd.read_csv(self.data_path)
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            print(f"✅ Loaded {len(self.df)} network traffic records")
        except FileNotFoundError:
            print(f"❌ Error: Could not find {self.data_path}")
            self.df = None
    
    def get_data_summary(self):
        """Get comprehensive data summary"""
        if self.df is None:
            return None
        
        anomalies = self.df[self.df['anomaly_prediction'] == -1]
        normal = self.df[self.df['anomaly_prediction'] != -1]
        
        return {
            "total_records": len(self.df),
            "total_anomalies": len(anomalies),
            "total_normal": len(normal),
            "anomaly_percentage": (len(anomalies) / len(self.df) * 100) if len(self.df) > 0 else 0,
            "severity": {
                "high": len(anomalies[anomalies['anomaly_score'] > 0.9]),
                "medium": len(anomalies[(anomalies['anomaly_score'] > 0.7) & (anomalies['anomaly_score'] <= 0.9)]),
                "low": len(anomalies[anomalies['anomaly_score'] <= 0.7])
            },
            "services": anomalies['service'].value_counts().head(10).to_dict() if not anomalies.empty else {},
            "protocols": anomalies['protocol_type'].value_counts().to_dict() if not anomalies.empty else {},
            "time_range": {
                "start": str(self.df['timestamp'].min()),
                "end": str(self.df['timestamp'].max())
            },
            "statistics": {
                "avg_anomaly_score": float(anomalies['anomaly_score'].mean()) if not anomalies.empty else 0,
                "max_anomaly_score": float(anomalies['anomaly_score'].max()) if not anomalies.empty else 0,
                "avg_src_bytes": float(anomalies['src_bytes'].mean()) if not anomalies.empty else 0,
                "avg_connection_count": float(anomalies['count'].mean()) if not anomalies.empty else 0
            }
        }
    
    def get_recent_alerts(self, hours=None, severity_threshold=0.0, limit=20):
        """Get recent security alerts"""
        if self.df is None:
            return []
        
        anomalies = self.df[self.df['anomaly_prediction'] == -1]
        anomalies = anomalies[anomalies['anomaly_score'] >= severity_threshold]
        
        if hours:
            cutoff = anomalies['timestamp'].max() - timedelta(hours=hours)
            anomalies = anomalies[anomalies['timestamp'] >= cutoff]
        
        recent = anomalies.sort_values('timestamp', ascending=False).head(limit)
        
        alerts = []
        for _, row in recent.iterrows():
            alerts.append({
                "timestamp": str(row['timestamp']),
                "src_ip": row['src_ip'],
                "dst_ip": row['dst_ip'],
                "service": row['service'],
                "protocol": row['protocol_type'],
                "score": float(row['anomaly_score']),
                "src_bytes": int(row['src_bytes']),
                "count": int(row['count']),
                "description": row.get('nlp_log', 'No description')
            })
        
        return alerts
    
    def analyze_attack_patterns(self):
        """Analyze attack patterns"""
        if self.df is None:
            return None
        
        anomalies = self.df[self.df['anomaly_prediction'] == -1]
        
        return {
            "patterns": {
                "data_exfiltration": len(anomalies[anomalies['src_bytes'] > 10000]),
                "dos_indicators": len(anomalies[anomalies['count'] > 50]),
                "failed_logins": len(anomalies[anomalies['num_failed_logins'] > 0]),
                "root_attempts": len(anomalies[anomalies['root_shell'] > 0]),
                "unauthorized_access": len(anomalies[anomalies['logged_in'] == 0])
            },
            "top_services": anomalies['service'].value_counts().head(10).to_dict(),
            "top_protocols": anomalies['protocol_type'].value_counts().to_dict(),
            "temporal_distribution": anomalies.groupby(anomalies['timestamp'].dt.hour)['anomaly_score'].count().to_dict()
        }
    
    def create_system_context(self):
        """Create system context for Claude"""
        summary = self.get_data_summary()
        patterns = self.analyze_attack_patterns()
        
        context = f"""You are an expert network security analyst working with data from a GHF-ART (Generalized Hierarchical Fuzzy Adaptive Resonance Theory) anomaly detection system deployed in a Security Operations Center (SOC).

CURRENT NETWORK STATUS:
======================
Total Traffic Events: {summary['total_records']:,}
Detected Anomalies: {summary['total_anomalies']:,} ({summary['anomaly_percentage']:.2f}%)
Normal Traffic: {summary['total_normal']:,}

THREAT SEVERITY DISTRIBUTION:
- 🔴 High Severity (Score > 0.9): {summary['severity']['high']:,} threats
- 🟡 Medium Severity (0.7-0.9): {summary['severity']['medium']:,} threats  
- 🟢 Low Severity (< 0.7): {summary['severity']['low']:,} threats

ATTACK PATTERNS IDENTIFIED:
- Data Exfiltration (>10KB transfers): {patterns['patterns']['data_exfiltration']:,}
- DoS Indicators (>50 connections): {patterns['patterns']['dos_indicators']:,}
- Failed Login Attempts: {patterns['patterns']['failed_logins']:,}
- Root Access Attempts: {patterns['patterns']['root_attempts']:,}
- Unauthorized Access: {patterns['patterns']['unauthorized_access']:,}

TOP TARGETED SERVICES:
{json.dumps(summary['services'], indent=2)}

PROTOCOL DISTRIBUTION:
{json.dumps(summary['protocols'], indent=2)}

STATISTICAL ANALYSIS:
- Average Anomaly Score: {summary['statistics']['avg_anomaly_score']:.4f}
- Maximum Anomaly Score: {summary['statistics']['max_anomaly_score']:.4f}
- Average Data Transfer (Anomalies): {summary['statistics']['avg_src_bytes']:.0f} bytes
- Average Connection Count: {summary['statistics']['avg_connection_count']:.1f}

MONITORING PERIOD:
From: {summary['time_range']['start']}
To: {summary['time_range']['end']}

Your role is to:
1. Provide clear, actionable security analysis
2. Explain threats in business terms while maintaining technical accuracy
3. Prioritize by severity and potential impact
4. Suggest concrete mitigation steps when relevant
5. Be concise but comprehensive
6. Use security industry terminology appropriately

Respond professionally as a senior SOC analyst would to security team members."""
        
        return context
    
    async def chat_with_claude(self, user_message):
        """
        Send message to Claude API and get response
        
        Args:
            user_message: User's question
            
        Returns:
            Claude's response
        """
        import aiohttp
        
        if not self.api_key:
            return self._fallback_response(user_message)
        
        try:
            system_context = self.create_system_context()
            
            # Prepare messages with conversation history
            messages = []
            
            # Add conversation history (last 5 exchanges)
            for msg in self.conversation_history[-10:]:
                if msg['role'] in ['user', 'assistant']:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                    "x-api-key": self.api_key
                }
                
                data = {
                    "model": self.model,
                    "max_tokens": 2000,
                    "system": system_context,
                    "messages": messages
                }
                
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['content'][0]['text']
                    else:
                        error_text = await response.text()
                        print(f"API Error: {response.status} - {error_text}")
                        return self._fallback_response(user_message)
        
        except Exception as e:
            print(f"Error calling Claude API: {str(e)}")
            return self._fallback_response(user_message)
    
    def _get_realtime_alerts(self):
        """Get real-time alerts from attack_alerts.json"""
        try:
            import json
            from pathlib import Path
            alert_file = Path('attack_alerts.json')
            if alert_file.exists():
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
                return alerts
        except:
            pass
        return []
    
    def _fallback_response(self, user_message):
        """Enhanced rule-based response system"""
        query_lower = user_message.lower().strip()
        
        # Get real-time alerts if available
        realtime_alerts = self._get_realtime_alerts()
        
        # Query classification with improved pattern matching
        if any(word in query_lower for word in ["summary", "overview", "status", "overall", "general"]):
            summary = self.get_data_summary()
            if summary is None:
                return "Unable to generate summary. Please ensure network logs are loaded."
            
            posture = "CRITICAL - Immediate attention required" if summary['severity']['high'] > 10 else "MODERATE - Monitor closely" if summary['total_anomalies'] > 50 else "STABLE - Normal operations"
            
            return f"""**Network Security Summary**

**Overall Status:**
- Total Events Monitored: {summary['total_records']:,}
- Anomalies Detected: {summary['total_anomalies']:,} ({summary['anomaly_percentage']:.2f}%)
- High Severity Threats: {summary['severity']['high']:,}
- Medium Severity: {summary['severity']['medium']:,}
- Low Severity: {summary['severity']['low']:,}

**Most Targeted Services:**
{', '.join([f"{k} ({v})" for k, v in list(summary['services'].items())[:5]]) if summary['services'] else 'None detected'}

**Security Posture:** {posture}

**Recommendation:** Focus on high-severity alerts first, then investigate unusual service targeting patterns."""
        
        elif any(word in query_lower for word in ["critical", "urgent", "high severity", "severe", "critical alerts"]):
            # Check real-time alerts first
            if realtime_alerts:
                critical_realtime = [a for a in realtime_alerts if a.get('severity') == 'CRITICAL']
                if critical_realtime:
                    response = f"**Critical Security Alerts** ({len(critical_realtime)} found in real-time monitoring)\n\n"
                    for i, alert in enumerate(critical_realtime[:10], 1):
                        timestamp = alert.get('timestamp', 'Unknown')
                        data = alert.get('data', {})
                        score = alert.get('attack_score', 0)
                        response += f"**Alert #{i}** - {timestamp}\n"
                        response += f"Source: {data.get('src_ip', 'N/A')} → Destination: {data.get('dst_ip', 'N/A')}\n"
                        response += f"Service: {data.get('service', 'N/A')} | Protocol: {data.get('protocol_type', 'N/A')}\n"
                        response += f"Attack Score: {score:.4f}\n"
                        response += f"Connection Count: {data.get('count', 'N/A')} | Source Bytes: {data.get('src_bytes', 0):,}\n\n"
                    return response
            
            # Fallback to historical data
            alerts = self.get_recent_alerts(severity_threshold=0.9, limit=10)
            if not alerts:
                return "**Critical Security Alerts**\n\nNo critical alerts found in the current dataset. The system is monitoring for threats."
            
            response = f"**Critical Security Alerts** ({len(alerts)} found)\n\n"
            for i, alert in enumerate(alerts[:10], 1):
                timestamp = alert.get('timestamp', 'Unknown')
                if isinstance(timestamp, str):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                response += f"**Alert #{i}** - {timestamp}\n"
                response += f"Source: {alert['src_ip']} → Destination: {alert['dst_ip']}\n"
                response += f"Service: {alert['service']} | Protocol: {alert['protocol']}\n"
                response += f"Severity Score: {alert['score']:.4f}\n"
                response += f"Connection Count: {alert.get('count', 'N/A')} | Source Bytes: {alert.get('src_bytes', 0):,}\n"
                if alert.get('description'):
                    desc = alert['description'][:200]
                    response += f"Details: {desc}\n"
                response += "\n"
            
            return response
        
        elif any(word in query_lower for word in ["pattern", "attack pattern", "attack type", "threat pattern", "attack vector"]):
            patterns = self.analyze_attack_patterns()
            if patterns is None:
                return "Unable to analyze attack patterns. Please ensure network logs are loaded."
            
            return f"""**Attack Pattern Analysis**

**Detected Attack Vectors:**
- Data Exfiltration Attempts: {patterns['patterns']['data_exfiltration']:,}
- DoS/DDoS Indicators: {patterns['patterns']['dos_indicators']:,}
- Failed Authentication: {patterns['patterns']['failed_logins']:,}
- Privilege Escalation: {patterns['patterns']['root_attempts']:,}
- Unauthorized Access: {patterns['patterns']['unauthorized_access']:,}

**Most Affected Services:**
{', '.join([f"{k} ({v})" for k, v in list(patterns['top_services'].items())[:5]]) if patterns['top_services'] else 'None detected'}

**Recommendation:** Investigate high-volume services for potential compromise. Review access logs for authentication failures."""
        
        elif any(word in query_lower for word in ["recent", "last", "hours", "today", "activity"]):
            # Extract time period
            hours = 1
            if any(x in query_lower for x in ["24", "day", "today"]):
                hours = 24
            elif any(x in query_lower for x in ["6", "six"]):
                hours = 6
            elif any(x in query_lower for x in ["2", "two"]):
                hours = 2
            
            alerts = self.get_recent_alerts(hours=hours, limit=20)
            
            high_severity = len([a for a in alerts if a['score'] > 0.9])
            services = len(set([a['service'] for a in alerts]))
            
            trend = "Increasing threat activity" if len(alerts) > 15 else "Stable threat level" if len(alerts) > 5 else "Low threat activity"
            
            response = f"""**Activity in Last {hours} Hour{'s' if hours > 1 else ''}**

**Statistics:**
- Total Alerts: {len(alerts)}
- High Severity: {high_severity}
- Affected Services: {services}
- Trend: {trend}

**Recent Critical Events:**\n"""
            
            if alerts:
                for a in alerts[:5]:
                    timestamp = a.get('timestamp', 'Unknown')
                    if isinstance(timestamp, str):
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.strftime("%H:%M:%S")
                        except:
                            pass
                    response += f"- [{timestamp}] {a['src_ip']} → {a['dst_ip']} via {a['service']} (Score: {a['score']:.3f})\n"
            else:
                response += "No alerts detected in this time period.\n"
            
            return response
        
        elif any(word in query_lower for word in ["service", "services", "targeted service", "which service"]):
            summary = self.get_data_summary()
            if summary and summary['services']:
                top_services = list(summary['services'].items())[:10]
                response = "**Most Targeted Services**\n\n"
                for i, (service, count) in enumerate(top_services, 1):
                    response += f"{i}. {service}: {count:,} attacks\n"
                return response
            return "No service targeting data available."
        
        elif any(word in query_lower for word in ["protocol", "protocols", "tcp", "udp", "icmp"]):
            summary = self.get_data_summary()
            if summary and summary['protocols']:
                response = "**Protocol Distribution in Attacks**\n\n"
                for protocol, count in summary['protocols'].items():
                    response += f"- {protocol.upper()}: {count:,} incidents\n"
                return response
            return "No protocol data available."
        
        elif any(word in query_lower for word in ["help", "what can", "how to", "commands", "capabilities"]):
            return """**Network Security ChatOps Assistant**

I can help you analyze network security data. Here are the types of queries I support:

**General Analysis:**
- "Give me a security status summary"
- "What's the overall threat level?"
- "Show me the security overview"

**Threat Investigation:**
- "Show critical alerts"
- "What attack patterns are detected?"
- "Analyze recent suspicious activity"
- "Show high severity threats"

**Time-Based Queries:**
- "What happened in the last 2 hours?"
- "Show me today's security events"
- "Recent activity in the last 6 hours"

**Specific Analysis:**
- "Which services are most targeted?"
- "Analyze protocol distribution"
- "Show attack patterns"
- "What protocols are being attacked?"

Type your question and I'll analyze the data for you."""
        
        else:
            # Default response with suggestions
            return """I understand you're asking about network security. I can help with:

- Security summaries and overall status
- Critical alerts and high-severity threats
- Attack pattern analysis
- Recent activity and time-based queries
- Service and protocol analysis

Try asking:
- "Show me critical alerts"
- "Give me a security summary"
- "What attack patterns are detected?"
- "Recent activity in the last 2 hours"

Or type "help" for more options."""
    
    def chat(self, user_message):
        """
        Synchronous chat interface - Uses rule-based AI (no API required)
        
        Args:
            user_message: User's question
            
        Returns:
            Response string
        """
        if self.df is None:
            return "⚠️ No data loaded. Please ensure 'network_logs_processed.csv' exists."
        
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now()
        })
        
        # Always use rule-based response (no API needed)
        response = self._fallback_response(user_message)
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })
        
        return response


if __name__ == "__main__":
    print("🛡️ Claude-Powered Network Security Chatbot")
    print("=" * 60)
    
    # Initialize
    chatbot = ClaudeSecurityChatbot()
    
    if chatbot.df is None:
        print("Error: Could not load data")
        exit(1)
    
    print("\nType 'exit' to quit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'exit':
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("\n🤖 AI Assistant: ", end="")
        response = chatbot.chat(user_input)
        print(response)
        print()
