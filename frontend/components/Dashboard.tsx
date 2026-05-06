'use client';
import { useState } from 'react';
import { evaluateVendor, getAlternatives } from '@/lib/api';

export default function Dashboard() {
  const [vendorName, setVendorName] = useState('');
  const [category, setCategory] = useState('IT');
  const [result, setResult] = useState<any>(null);
  const [alternatives, setAlternatives] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const data = await evaluateVendor(vendorName, category);
      setResult(data);
      const alt = await getAlternatives(data.id);
      setAlternatives(alt);
    } catch (e) {
      alert('Evaluation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{padding:40,maxWidth:800}}>
      <div style={{display:'flex',gap:12,marginBottom:24}}>
        <input placeholder="Vendor name" value={vendorName} onChange={e => setVendorName(e.target.value)}
          style={{padding:'10px 16px',borderRadius:8,border:'1px solid #334155',background:'#1e293b',color:'#f8fafc',minWidth:200}} />
        <select value={category} onChange={e => setCategory(e.target.value)}
          style={{padding:'10px 16px',borderRadius:8,border:'1px solid #334155',background:'#1e293b',color:'#f8fafc'}}>
          <option value="IT">IT</option>
          <option value="Services">Services</option>
          <option value="Logistics">Logistics</option>
        </select>
        <button onClick={handleEvaluate} disabled={loading}
          style={{padding:'10px 20px',borderRadius:8,border:'none',background:'#059669',color:'#fff',cursor:'pointer'}}>
          {loading ? 'Evaluating...' : 'Evaluate Vendor'}
        </button>
      </div>

      {result && (
        <div style={{display:'grid',gap:16}}>
          <div style={{padding:20,borderRadius:12,background:'#1e293b',border:'1px solid #334155'}}>
            <h3 style={{marginBottom:12,color:'#059669'}}>Vendor Evaluation Result</h3>
            <p><strong>Vendor:</strong> {result.vendor_name}</p>
            <p><strong>Category:</strong> {result.category}</p>
            <p><strong>Overall score:</strong> {result.overall_score}</p>
            <p><strong>Risk rating:</strong> {result.risk_rating}</p>
            <p><strong>Performance history:</strong> {result.performance_history?.join(', ')}</p>
            <p><strong>Renewal recommendation:</strong> {result.renewal_recommendation}</p>
          </div>
          {alternatives.length > 0 && (
            <div style={{padding:20,borderRadius:12,background:'#1e293b',border:'1px solid #334155'}}>
              <h3 style={{marginBottom:12,color:'#059669'}}>Alternative Vendors</h3>
              {alternatives.map((alt, i) => (
                <p key={i}><strong>{alt.name}</strong> — Score: {alt.score}, Risk: {alt.risk}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
