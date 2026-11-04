import {useState} from "react"; import {upload} from "../api";
export function UploadPage({done}:{done:()=>void}) { const [file,setFile]=useState<File>(); const [title,setTitle]=useState(""); const [message,setMessage]=useState("");
 async function submit(e:React.FormEvent){e.preventDefault(); if(!file)return; try {const r=await upload(file,title);setMessage(`Uploaded: ${r.video_id}`);done()}catch(e){setMessage(String(e))}}
 return <section><h2>Upload video</h2><form onSubmit={submit}><input placeholder="Title (optional)" value={title} onChange={e=>setTitle(e.target.value)}/><input type="file" accept="video/mp4,video/quicktime,video/x-matroska,video/webm" onChange={e=>setFile(e.target.files?.[0])}/><button>Upload</button></form><p>{message}</p></section> }
