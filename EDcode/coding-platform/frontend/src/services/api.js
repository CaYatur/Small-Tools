import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // Adjust the base URL as needed

export const executePythonCode = async (code, packages) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/execute`, { code, packages });
        return response.data;
    } catch (error) {
        console.error('Error executing Python code:', error);
        throw error;
    }
};

export const installPythonPackage = async (packageName) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/packages/install`, { packageName });
        return response.data;
    } catch (error) {
        console.error('Error installing Python package:', error);
        throw error;
    }
};

export const executeCSharpCode = async (code, packages) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/csharp/execute`, { code, packages });
        return response.data;
    } catch (error) {
        console.error('Error executing C# code:', error);
        throw error;
    }
};

export const installCSharpPackage = async (packageName) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/csharp/packages/install`, { packageName });
        return response.data;
    } catch (error) {
        console.error('Error installing C# package:', error);
        throw error;
    }
};