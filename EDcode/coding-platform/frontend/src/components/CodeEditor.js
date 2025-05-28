import React, { useState } from 'react';
import { Controlled as CodeMirror } from 'react-codemirror2';
import 'codemirror/lib/codemirror.css';
import 'codemirror/mode/javascript/javascript'; // Change mode based on the language

const CodeEditor = () => {
    const [code, setCode] = useState('// Write your code here');

    const handleCodeChange = (editor, data, value) => {
        setCode(value);
    };

    return (
        <div>
            <CodeMirror
                value={code}
                options={{
                    lineNumbers: true,
                    mode: 'javascript', // Change mode based on the language
                    theme: 'default',
                }}
                onBeforeChange={handleCodeChange}
            />
        </div>
    );
};

export default CodeEditor;