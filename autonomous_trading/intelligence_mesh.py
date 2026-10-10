# autonomous_trading/intelligence_mesh.py
"""
Intelligence Mesh for the Autonomous Trading Ecosystem.
Orchestrates AI agents to analyze market data and generate trading signals.
Integrates with OpenRouter to utilize uncensored or highly capable LLMs (e.g. Llama 3, DeepSeek).
"""

import os
import json
import requests
from typing import Dict, Any, List
# New agents for macro and on-chain data
from autonomous_trading.macro_agent import MacroEconomicAgent
from autonomous_trading.onchain_agent import OnChainAgent
from autonomous_trading.social_sentiment_agent import SocialSentimentAgent

class OpenRouterClient:
    """A lightweight client for OpenRouter to access various LLMs."""
    
    def __init__(self, api_key: str = None):
        # Fallback to an env var if not explicitly provided
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8888", # Required by OpenRouter
            "X-Title": "AutonomousTradingEcosystem", # Required by OpenRouter
            "Content-Type": "application/json"
        }

    def generate_completion(self, prompt: str, model: str = "meta-llama/llama-3-8b-instruct:free", system_prompt: str = "") -> str:
        """Call the OpenRouter API."""
        if not self.api_key:
            return '{"error": "No OpenRouter API key provided. Set OPENROUTER_API_KEY environment variable."}'
            
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"} # Enforce JSON output for deterministic parsing
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return json.dumps({"error": str(e), "status": "failed"})

class MarketAnalystAgent:
    """Agent responsible for analyzing raw market data and producing a structured summary."""
    
    def __init__(self, llm_client: OpenRouterClient):
        self.llm = llm_client
        self.system_prompt = (
            "You are a highly capable quantitative market analyst. "
            "Your job is to analyze raw market data and produce a JSON summary of market conditions. "
            "Output valid JSON ONLY."
        )
        
    def analyze(self, raw_data: str) -> Dict[str, Any]:
        prompt = f"Analyze the following market data and summarize the trend (bullish/bearish/neutral), volatility (low/medium/high), and key support/resistance levels. Output JSON.\n\nData: {raw_data}"
        result_str = self.llm.generate_completion(prompt, system_prompt=self.system_prompt)
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {"error": "Analyst output was not valid JSON", "raw_output": result_str}

class NewsSentimentAgent:
    """Agent responsible for analyzing qualitative sentiment."""
    
    def __init__(self, llm_client: OpenRouterClient):
        self.llm = llm_client
        self.system_prompt = (
            "You are a market sentiment analyst. "
            "Your job is to read raw headlines or social data and determine the overall sentiment. "
            "Output valid JSON ONLY with keys 'sentiment' (bullish/bearish/neutral) and 'score' (0-100)."
        )
        
    def analyze(self, symbol: str) -> Dict[str, Any]:
        # For simulation, we ask the LLM to provide a general simulated sentiment.
        prompt = f"Provide a simulated current market sentiment analysis for {symbol}. Output JSON."
        result_str = self.llm.generate_completion(prompt, system_prompt=self.system_prompt)
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {"error": "Sentiment output was not valid JSON", "raw_output": result_str}

class StrategicReasoningAgent:
    """Agent responsible for deciding on a trade based on the analyst's summary."""
    
    def __init__(self, llm_client: OpenRouterClient):
        self.llm = llm_client
        self.system_prompt = (
            "You are an aggressive but mathematically rigorous trading strategist. "
            "Based on market analysis, you must decide whether to BUY, SELL, or HOLD. "
            "You MUST output valid JSON ONLY with the keys: 'action' (BUY/SELL/HOLD), 'confidence' (0-100), and 'reasoning' (string)."
        )
        
    def generate_signal(self, analysis: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        prompt = f"Target Asset: {symbol}\nMarket Analysis: {json.dumps(analysis)}\n\nGenerate a trading signal. Output JSON."
        result_str = self.llm.generate_completion(prompt, system_prompt=self.system_prompt)
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {"action": "HOLD", "error": "Strategist output was not valid JSON", "raw_output": result_str}

class SwarmOrchestrator:
    """Orchestrates the flow of data through the AI agents."""
    
    def __init__(self, api_key: str = None):
        self.client = OpenRouterClient(api_key)
        self.analyst = MarketAnalystAgent(self.client)
        self.sentiment = NewsSentimentAgent(self.client)
        self.strategist = StrategicReasoningAgent(self.client)
        # Instantiate macro and on-chain agents
        self.macro = MacroEconomicAgent()
        self.onchain = OnChainAgent()
        self.social = SocialSentimentAgent()
        
    def process_market_tick(self, symbol: str, raw_data: str) -> Dict[str, Any]:
        """Runs the multi-agent swarm on new market data to generate a signal."""
        print(f"[{symbol}] Swarm Orchestrator: Initiating Market Analyst...")
        analysis = self.analyst.analyze(raw_data)
        
        if "error" in analysis:
             print(f"[{symbol}] Analyst Error: {analysis['error']}")
             return {"action": "HOLD", "reasoning": "Analyst failure"}
             
        print(f"[{symbol}] Swarm Orchestrator: Initiating Sentiment Analyst...")
        sentiment_data = self.sentiment.analyze(symbol)
        
        print(f"[{symbol}] Swarm Orchestrator: Initiating Macro Economic Analyst...")
        macro_data = self.macro.get_macro_snapshot()
        
        print(f"[{symbol}] Swarm Orchestrator: Initiating On-Chain Analyst...")
        onchain_data = self.onchain.get_onchain_snapshot()
        social_data = self.social.analyze(symbol)
        
        # Combine all analyses
        combined_analysis = {
            "technical": analysis,
            "sentiment": sentiment_data,
            "macro": macro_data,
            "onchain": onchain_data,
            "social": social_data
        }
             
        print(f"[{symbol}] Swarm Orchestrator: Initiating Strategist...")
        signal = self.strategist.generate_signal(combined_analysis, symbol)
        
        return signal
