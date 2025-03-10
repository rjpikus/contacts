'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useContactsStore, useGroupsStore, Contact } from '@/lib/store';
import { toast } from 'react-toastify';
import Link from 'next/link';
import { FiPlus, FiSearch, FiDownload, FiUpload, FiEdit, FiTrash2 } from 'react-icons/fi';
import axios from 'axios';

export default function Contacts() {
  const { contacts, loading, fetchContacts, searchContacts, filterByGroup, deleteContact } = useContactsStore();
  const { groups, fetchGroups } = useGroupsStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const router = useRouter();
  
  useEffect(() => {
    fetchContacts();
    fetchGroups();
  }, [fetchContacts, fetchGroups]);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    searchContacts(searchTerm);
  };
  
  const handleGroupFilter = (groupName: string | null) => {
    filterByGroup(groupName);
  };
  
  const handleDeleteClick = (contact: Contact) => {
    setSelectedContact(contact);
    setShowDeleteModal(true);
  };
  
  const confirmDelete = async () => {
    if (!selectedContact) return;
    
    try {
      await deleteContact(selectedContact.id);
      toast.success('Contact deleted successfully');
      setShowDeleteModal(false);
    } catch (error) {
      toast.error('Failed to delete contact');
    }
  };
  
  const handleExport = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Not authenticated');
      
      const response = await axios.get('/api/contacts/export', {
        headers: {
          Authorization: `Bearer ${token}`
        },
        responseType: 'blob'
      });
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'contacts.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Contacts exported successfully');
    } catch (error) {
      toast.error('Failed to export contacts');
    }
  };
  
  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';
    
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const token = localStorage.getItem('token');
        if (!token) throw new Error('Not authenticated');
        
        await axios.post('/api/contacts/import', formData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        
        toast.success('Contacts imported successfully');
        fetchContacts();
      } catch (error) {
        toast.error('Failed to import contacts');
      }
    };
    
    input.click();
  };
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Contacts</h1>
        <div className="flex space-x-2">
          <button
            onClick={handleImport}
            className="flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            <FiUpload className="mr-2" />
            Import
          </button>
          <button
            onClick={handleExport}
            className="flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            <FiDownload className="mr-2" />
            Export
          </button>
          <Link
            href="/contacts/new"
            className="flex items-center px-3 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600"
          >
            <FiPlus className="mr-2" />
            Add Contact
          </Link>
        </div>
      </div>
      
      <div className="flex flex-col md:flex-row gap-6 mb-6">
        {/* Search */}
        <div className="md:w-2/3">
          <form onSubmit={handleSearch} className="flex">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search contacts..."
              className="flex-grow px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-primary-500 text-white rounded-r-md hover:bg-primary-600"
            >
              <FiSearch />
            </button>
          </form>
        </div>
        
        {/* Group Filter */}
        <div className="md:w-1/3">
          <select
            onChange={(e) => handleGroupFilter(e.target.value || null)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Contacts</option>
            {groups.map(group => (
              <option key={group.id} value={group.name}>
                {group.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Contacts List */}
      {loading ? (
        <div className="text-center py-8">Loading contacts...</div>
      ) : contacts.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No contacts found</p>
          <Link href="/contacts/new" className="text-primary-500 hover:underline mt-2 inline-block">
            Add your first contact
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Phone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Groups
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {contacts.map(contact => (
                <tr key={contact.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">
                      {contact.first_name} {contact.last_name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                    {contact.email || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                    {contact.phone || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-wrap gap-1">
                      {contact.groups.length > 0 ? (
                        contact.groups.map(group => (
                          <span
                            key={group.id}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800"
                          >
                            {group.name}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <Link
                        href={`/contacts/${contact.id}`}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        <FiEdit />
                      </Link>
                      <button
                        onClick={() => handleDeleteClick(contact)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <FiTrash2 />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium mb-4">Confirm Delete</h3>
            <p className="mb-6">
              Are you sure you want to delete {selectedContact?.first_name} {selectedContact?.last_name}? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 