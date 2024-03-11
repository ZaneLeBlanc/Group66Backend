{/* Zane - instructions to start: (also have Python installed on your machine or this won't work)
1. open 2 terminals, one in /Frontend and one in /Backend
2. in the /Frontend terminal, run 'npm i'
3. in the /Backend terminal, run 'pip install flask' and 'pip install flask-cors'
4. in the /Backend terminal, run 'python test.py' (or whatever the file is named)
5. in the /Frontend terminal, run 'npm run dev'
6. it should run in a new browser tab and you can click the echo button to make sure it works */}


import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios';

function App() {
  {/* React variables */}
  const [pythonCode, setPythonCode] = useState('bruh');
  const [result, setResult] = useState('');

  {/* This function runs whenever the echo button is clicked,
    it sends the user given string to the python server and stores
    the modified string received within 'result' and displays that */}
  const executePythonCode = async () => {
    try {
      const response = await axios.post('http://localhost:5000/run-python-code', { code: pythonCode });

      setResult(response.data.result);
    } catch (error) {
      console.error('Error executing Python code:', error);
    }
  };

  {/* App itself */}
  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>

      <h1>ML Intrusion Detection Tool</h1>
        
      <div className="testSection">
        <textarea value={pythonCode} onChange={(e) => setPythonCode(e.target.value)} />
        <button onClick={executePythonCode}>echo to Python code</button>
        <div>Result: {result}</div>
      </div>

    </>
  )
}

export default App
