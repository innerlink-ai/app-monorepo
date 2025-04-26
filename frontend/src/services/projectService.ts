// projectService.ts
import { axios } from '../composables/index';
import { config } from '@/config';

const BASE_URL = config.apiUrl;

export interface Collection {
  id: string;
  name: string;
  description?: string;
}

export interface FileAttachment {
  name: string;
  content: string;
  file_type?: string;
}

export interface ProjectDocument {
  doc_id: string;
  name: string;
  file_type?: string;
}

export interface ProjectData {
  name: string;
  custom_instructions?: string;
  collections?: Collection[];
  documents?: FileAttachment[];
}

export interface ProjectResponse {
  project_id: string;
  name: string;
  custom_instructions?: string;
  created_at: string;
  updated_at: string;
  documents: ProjectDocument[];
  collections: Collection[];
}

export const createProject = async (payload: ProjectData): Promise<ProjectResponse> => {
  try {
    console.log("Inside createProject service function. Payload:", payload);
    const response = await axios.post(
      `${BASE_URL}/projects`,
      payload,
      { withCredentials: true }
    );
    console.log("axios.post successful:", response);
    return response.data;
  } catch (error: any) {
    console.error("Error creating project (in projectService.ts):", error);
    if (error.response) {
        console.error("Axios response error:", error.response.data, error.response.status, error.response.headers);
    } else if (error.request) {
        console.error("Axios request error:", error.request);
    } else {
        console.error('Error message:', error.message);
    }
    throw new Error(error.response?.data?.detail || "Failed to create project");
  }
};

export const getProjects = async (): Promise<ProjectResponse[]> => {
  try {
    const response = await axios.get(
      `${BASE_URL}/projects`,
      { withCredentials: true }
    );
    return response.data;
  } catch (error: any) {
    console.error("Error fetching projects:", error);
    throw new Error(error.response?.data?.detail || "Failed to fetch projects");
  }
};

export const getProject = async (projectId: string): Promise<ProjectResponse> => {
  try {
    const response = await axios.get(
      `${BASE_URL}/projects/${projectId}`,
      { withCredentials: true }
    );
    return response.data;
  } catch (error: any) {
    console.error(`Error fetching project ${projectId}:`, error);
    throw new Error(error.response?.data?.detail || "Failed to fetch project");
  }
};

export const updateProject = async (projectId: string, updates: Partial<ProjectData>): Promise<ProjectResponse> => {
  try {
    const response = await axios.put(
      `${BASE_URL}/projects/${projectId}`,
      updates,
      { withCredentials: true }
    );
    return response.data;
  } catch (error: any) {
    console.error(`Error updating project ${projectId}:`, error);
    throw new Error(error.response?.data?.detail || "Failed to update project");
  }
};

export const deleteProject = async (projectId: string): Promise<void> => {
  try {
    await axios.delete(
      `${BASE_URL}/projects/${projectId}`,
      { withCredentials: true }
    );
  } catch (error: any) {
    console.error(`Error deleting project ${projectId}:`, error);
    throw new Error(error.response?.data?.detail || "Failed to delete project");
  }
};

export const addDocumentToProject = async (projectId: string, document: FileAttachment): Promise<ProjectDocument> => {
  try {
    const response = await axios.post(
      `${BASE_URL}/projects/${projectId}/documents`,
      document,
      { withCredentials: true }
    );
    return response.data;
  } catch (error: any) {
    console.error(`Error adding document to project ${projectId}:`, error);
    throw new Error(error.response?.data?.detail || "Failed to add document to project");
  }
};

export const deleteDocumentFromProject = async (projectId: string, docId: string): Promise<void> => {
  try {
    await axios.delete(
      `${BASE_URL}/projects/${projectId}/documents/${docId}`,
      { withCredentials: true }
    );
  } catch (error: any) {
    console.error(`Error deleting document ${docId} from project ${projectId}:`, error);
    throw new Error(error.response?.data?.detail || "Failed to delete document");
  }
};

export const linkChatToProject = async (projectId: string, chatId: string): Promise<void> => {
  try {
    await axios.post(
      `${BASE_URL}/projects/${projectId}/chats/${chatId}`,
      {},
      { withCredentials: true }
    );
  } catch (error: any) {
    console.error(`Error linking chat ${chatId} to project ${projectId}:`, error);
    throw new Error(error.response?.data?.detail || "Failed to link chat to project");
  }
};


export const getProjectChats = async (projectId: string): Promise<any[]> => {
  try {
    const response = await axios.get(
      `${BASE_URL}/projects/${projectId}/chats`,
      { withCredentials: true }
    );
    return response.data;
  } catch (error: any) {
    console.error(`Error fetching chats for project ${projectId}:`, error);
    throw new Error(error.response?.data?.detail || "Failed to fetch project chats");
  }
};