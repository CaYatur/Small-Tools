import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import CodeEditor from './components/CodeEditor';
import Console from './components/Console';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <div>
        <Navbar />
        <Switch>
          <Route path="/" exact component={CodeEditor} />
          <Route path="/console" component={Console} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;