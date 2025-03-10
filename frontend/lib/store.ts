import { create } from 'zustand';
import axios from 'axios';

// Types
export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Contact {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  groups: Group[];
}

export interface Group {
  id: number;
  name: string;
  user_id?: number;
  contacts_count?: number;
}

// Auth Store Interface
interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  checkAuth: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

// Create Auth Store
export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  
  checkAuth: async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        set({ isAuthenticated: false, user: null });
        return;
      }
      
      const response = await axios.get('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      set({ isAuthenticated: true, user: response.data });
    } catch (error) {
      localStorage.removeItem('token');
      set({ isAuthenticated: false, user: null });
    }
  },
  
  login: async (email, password) => {
    try {
      const response = await axios.post('/api/auth/login', { email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      
      // Get user data
      const userResponse = await axios.get('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${access_token}`
        }
      });
      
      set({ isAuthenticated: true, user: userResponse.data });
    } catch (error) {
      throw error;
    }
  },
  
  register: async (email, password) => {
    try {
      await axios.post('/api/auth/register', { email, password });
      // After registration, log in
      await useAuthStore.getState().login(email, password);
    } catch (error) {
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    set({ isAuthenticated: false, user: null });
  }
}));

// Contacts Store Interface
interface ContactsState {
  contacts: Contact[];
  filteredContacts: Contact[];
  searchTerm: string;
  selectedGroup: string | null;
  loading: boolean;
  fetchContacts: () => Promise<void>;
  searchContacts: (term: string) => void;
  filterByGroup: (groupName: string | null) => void;
  addContact: (contactData: Partial<Contact>) => Promise<void>;
  updateContact: (id: number, contactData: Partial<Contact>) => Promise<void>;
  deleteContact: (id: number) => Promise<void>;
}

// Create Contacts Store
export const useContactsStore = create<ContactsState>((set, get) => ({
  contacts: [],
  filteredContacts: [],
  searchTerm: '',
  selectedGroup: null,
  loading: false,
  
  fetchContacts: async () => {
    try {
      set({ loading: true });
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No auth token');
      }
      
      const queryParams = new URLSearchParams();
      if (get().searchTerm) {
        queryParams.append('search', get().searchTerm);
      }
      if (get().selectedGroup) {
        queryParams.append('group', get().selectedGroup);
      }
      
      const response = await axios.get(`/api/contacts?${queryParams.toString()}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      set({ 
        contacts: response.data.contacts,
        filteredContacts: response.data.contacts,
        loading: false
      });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },
  
  searchContacts: (term) => {
    set({ searchTerm: term });
    get().fetchContacts();
  },
  
  filterByGroup: (groupName) => {
    set({ selectedGroup: groupName });
    get().fetchContacts();
  },
  
  addContact: async (contactData) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No auth token');
      }
      
      await axios.post('/api/contacts', contactData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      await get().fetchContacts();
    } catch (error) {
      throw error;
    }
  },
  
  updateContact: async (id, contactData) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No auth token');
      }
      
      await axios.put(`/api/contacts/${id}`, contactData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      await get().fetchContacts();
    } catch (error) {
      throw error;
    }
  },
  
  deleteContact: async (id) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No auth token');
      }
      
      await axios.delete(`/api/contacts/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      await get().fetchContacts();
    } catch (error) {
      throw error;
    }
  }
}));

// Groups Store Interface
interface GroupsState {
  groups: Group[];
  loading: boolean;
  fetchGroups: () => Promise<void>;
  addGroup: (name: string) => Promise<void>;
  updateGroup: (id: number, name: string) => Promise<void>;
  deleteGroup: (id: number) => Promise<void>;
}

// Create Groups Store
export const useGroupsStore = create<GroupsState>((set, get) => ({
  groups: [],
  loading: false,
  
  fetchGroups: async () => {
    try {
      set({ loading: true });
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No auth token');
      }
      
      const response = await axios.get('/api/groups', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      set({ groups: response.data.groups, loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },
  
  addGroup: async (name) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No auth token');
      }
      
      await axios.post('/api/groups', { name }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      await get().fetchGroups();
    } catch (error) {
      throw error;
    }
  },
  
  updateGroup: async (id, name) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No auth token');
      }
      
      await axios.put(`/api/groups/${id}`, { name }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      await get().fetchGroups();
    } catch (error) {
      throw error;
    }
  },
  
  deleteGroup: async (id) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No auth token');
      }
      
      await axios.delete(`/api/groups/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      await get().fetchGroups();
    } catch (error) {
      throw error;
    }
  }
})); 