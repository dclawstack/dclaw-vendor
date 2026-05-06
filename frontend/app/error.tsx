'use client';
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div style={{padding:40,color:'#ef4444'}}>
      <h2>Something went wrong</h2>
      <button onClick={reset} style={{marginTop:12,padding:'8px 16px',borderRadius:6,border:'none',background:'#334155',color:'#fff',cursor:'pointer'}}>Try again</button>
    </div>
  );
}
