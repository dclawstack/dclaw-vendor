import { Handshake } from 'lucide-react';
export default function Header() {
  return (
    <header style={{display:'flex',alignItems:'center',gap:12,padding:'20px 40px',borderBottom:'1px solid #1e293b'}}>
      <Handshake color="#059669" size={28} />
      <div>
        <h1 style={{fontSize:20,fontWeight:700,color:'#f8fafc'}}>DClaw Vendor</h1>
        <p style={{fontSize:12,color:'#94a3b8'}}>Vendor evaluation and management</p>
      </div>
    </header>
  );
}
