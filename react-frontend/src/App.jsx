import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [mode, setMode] = useState("quick");
  const [rawText, setRawText] = useState('');
  const [toneStyle, setToneStyle] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [maxLength, setMaxLength] = useState(1000);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [campaignBrief, setCampaignBrief] = useState({
    product: '',
    target_audience: '',
    goals: '',
    key_features: '',
    budget: '',
    timeline: ''
  });

  const handleGenerate = async () => {
    setLoading(true);
    try {
      let response;

      if (mode === "quick") {
        response = await axios.post("http://localhost:5000/generate", {
          raw_text: rawText,
          tone_style: toneStyle || null,
          temperature,
          max_length: maxLength
        });
      } else {
        const brief = {
          ...campaignBrief,
          goals: campaignBrief.goals.split(",").map(g => g.trim()),
          key_features: campaignBrief.key_features.split(",").map(k => k.trim())
        };

        response = await axios.post("http://localhost:5000/run_campaign", {
          campaign_brief: brief
        });
      }

      setResult(response.data);
    } catch (err) {
      setResult({ error: err.response?.data?.error || "Request Failed" });
    }
    setLoading(false);
  };

  return (
    <div style={{
          fontFamily: 'Arial',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-start',
          alignItems: 'center',
          minHeight: '100vh',
          width: '100vw',
          paddingTop: 40,
          backgroundColor: '#f5f5f5',
          boxSizing: 'border-box'
        }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>Intelligent Ad Generation System</h1>

      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <button
          onClick={() => setMode("quick")}
          style={{
            backgroundColor: mode === "quick" ? "#007bff" : "#ccc",
            color: "#fff",
            border: "none",
            padding: "10px 20px",
            marginRight: 10,
            cursor: "pointer"
          }}
        >
          Ad Generation
        </button>
        <button
          onClick={() => setMode("campaign")}
          style={{
            backgroundColor: mode === "campaign" ? "#007bff" : "#ccc",
            color: "#fff",
            border: "none",
            padding: "10px 20px",
            cursor: "pointer"
          }}
        >
          pdf advertisement generation
        </button>
      </div>

      <div style={{ border: "1px solid #ddd", borderRadius: 10, padding: 20, marginBottom: 20, background: "#f9f9f9" }}>
        {mode === "quick" ? (
          <>
            <h3>Quick Copy Entry</h3>
            <textarea
              rows={4}
              style={{ width: '100%', marginBottom: 10 }}
              placeholder="Please enter a product description or user review..."
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
            />
            <input
              placeholder="Advertising tone style (optional)"
              value={toneStyle}
              onChange={(e) => setToneStyle(e.target.value)}
              style={{ width: '100%', marginBottom: 10 }}
            />
            <label>temperature coefficient: {temperature}</label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              style={{ width: '100%', marginBottom: 10 }}
            />
            <label>Maximum Output Length:</label>
            <input
              type="number"
              value={maxLength}
              onChange={(e) => setMaxLength(parseInt(e.target.value))}
              style={{ width: '100%' }}
            />
          </>
        ) : (
          <>
            <h3>Advertising campaign information</h3>
            <input
              placeholder="product name"
              value={campaignBrief.product}
              onChange={(e) => setCampaignBrief({ ...campaignBrief, product: e.target.value })}
              style={{ width: '100%', marginBottom: 8 }}
            />
            <input
              placeholder="target user"
              value={campaignBrief.target_audience}
              onChange={(e) => setCampaignBrief({ ...campaignBrief, target_audience: e.target.value })}
              style={{ width: '100%', marginBottom: 8 }}
            />
            <input
              placeholder="Objectives (separated by English commas)"
              value={campaignBrief.goals}
              onChange={(e) => setCampaignBrief({ ...campaignBrief, goals: e.target.value })}
              style={{ width: '100%', marginBottom: 8 }}
            />
            <input
              placeholder="Key selling points (separated by English commas)"
              value={campaignBrief.key_features}
              onChange={(e) => setCampaignBrief({ ...campaignBrief, key_features: e.target.value })}
              style={{ width: '100%', marginBottom: 8 }}
            />
            <input
              placeholder="budget"
              value={campaignBrief.budget}
              onChange={(e) => setCampaignBrief({ ...campaignBrief, budget: e.target.value })}
              style={{ width: '100%', marginBottom: 8 }}
            />
            <input
              placeholder="time cycle"
              value={campaignBrief.timeline}
              onChange={(e) => setCampaignBrief({ ...campaignBrief, timeline: e.target.value })}
              style={{ width: '100%' }}
            />
          </>
        )}
      </div>

      <div style={{ textAlign: 'center' }}>
        <button onClick={handleGenerate} disabled={loading} style={{
          backgroundColor: "#28a745",
          color: "#fff",
          border: "none",
          padding: "10px 30px",
          fontSize: 16,
          cursor: "pointer",
          borderRadius: 5
        }}>
          {loading ? "in the process of being generated..." : "Generate ads"}
        </button>
      </div>

      {result && (
        <div style={{ marginTop: 30, border: "1px solid #eee", padding: 20, borderRadius: 10, background: "#fff" }}>
          {result.error ? (
            <p style={{ color: 'red' }}>error：{result.error}</p>
          ) : mode === "quick" ? (
            <>
              <h2>Ad copy results</h2>
              <p><strong>{result.ad_text}</strong></p>
              <h3>Extraction of information</h3>
              <ul>
                <li>product name：{result.extracted_info.product_name}</li>
                <li>product description：{result.extracted_info.product_description}</li>
                <li>emotion：{result.extracted_info.emotion}</li>
                <li>interest ：{(result.extracted_info.interests || []).join(', ')}</li>
                <li>budget conscious：{result.extracted_info.budget_conscious ? '是' : '否'}</li>
                <li>age group：{result.extracted_info.age_group}</li>
                <li>selected tone：{result.selected_tone}</li>
              </ul>
            </>
          ) : (
            <>
              <h2>Advertising Creative Process Results</h2>
              <p><strong>strategy proposal：</strong> {result.strategy}</p>
              <p><strong>Creative Concept：</strong> {result.creative_concepts}</p>
              <p><strong>copywriter：</strong> {result.copy}</p>
              <p><strong>Image link：</strong> <a href={result.image_url} target="_blank" rel="noreferrer">View Pictures</a></p>
              <h3>analysis</h3>
              <pre style={{ whiteSpace: 'pre-wrap', background: '#f0f0f0', padding: 10 }}>
                {JSON.stringify(result.analytics_report, null, 2)}
              </pre>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default App;
