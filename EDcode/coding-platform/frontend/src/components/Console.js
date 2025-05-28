import React from 'react';

const Console = ({ output }) => {
    return (
        <div className="console">
            <h2>Console Output</h2>
            <pre>{output}</pre>
        </div>
    );
};

export default Console;