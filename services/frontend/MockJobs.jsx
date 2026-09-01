import React, {useEffect, useState} from 'react'
import './mockJobs.css'

export default function MockJobs({apiUrl = '/posts/mock_jobs'}){
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(()=>{
    let mounted = true
    fetch(apiUrl)
      .then(r=> r.ok ? r.json() : Promise.reject(r.status))
      .then(data => { if(mounted) setJobs(data) })
      .catch(()=>{
        // fallback sample data when API is not available
        if(mounted) setJobs([
          {title:'Software Engineering Intern', company:'Acme Corp', location:'San Francisco, CA', required_skills:['Python','SQL'], url:'#', source:'Mock'},
          {title:'Frontend Engineer', company:'Beta Labs', location:'Remote', required_skills:['React','CSS'], url:'#', source:'Mock'},
          {title:'Data Science Intern', company:'Gamma Analytics', location:'New York, NY', required_skills:['pandas','SQL'], url:'#', source:'Mock'}
        ])
      })
      .finally(()=>{ if(mounted) setLoading(false) })
    return ()=> { mounted = false }
  }, [apiUrl])

  if(loading) return <div className="mock-jobs-loading">Loading jobs…</div>

  return (
    <div className="mock-jobs-grid">
      {jobs.map((job, idx) => (
        <article className="mock-job-card" key={idx}>
          <div className="mock-job-header">
            <h3 className="mock-job-title"><a href={job.url || '#'} target="_blank" rel="noreferrer">{job.title}</a></h3>
            <div className="mock-job-company">{job.company}</div>
          </div>
          <div className="mock-job-meta">
            <span className="mock-job-location">{job.location || 'Remote'}</span>
            <span className="mock-job-term">{job.term || ''}</span>
          </div>
          <p className="mock-job-skills">{(job.required_skills||[]).slice(0,4).join(' • ')}</p>
          <div className="mock-job-footer">
            <span className="mock-job-source">{job.source}</span>
            <a className="mock-job-visit" href={job.url || '#'} target="_blank" rel="noreferrer">View</a>
          </div>
        </article>
      ))}
    </div>
  )
}
