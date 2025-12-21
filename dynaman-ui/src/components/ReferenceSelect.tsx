import React, { useState, useEffect, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import api from '@/lib/api';

interface ReferenceSelectProps {
  entityName: string; // The entity name this field references
  value: string; // The currently selected ID
  onChange: (value: string) => void;
  label?: string;
  placeholder?: string;
  required?: boolean;
}

interface ReferencedRecord {
  id: string;
  [key: string]: any; // Allow other properties
}

export default function ReferenceSelect({
  entityName,
  value,
  onChange,
  label,
  placeholder,
  required = false,
}: ReferenceSelectProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [options, setOptions] = useState<ReferencedRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500); // 500ms debounce
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch options based on entityName and debouncedSearchTerm
  useEffect(() => {
    if (!entityName) {
      setOptions([]);
      return;
    }

    const fetchOptions = async () => {
      setLoading(true);
      setError(null);
      try {
        let url = `/data/${entityName}`;
        const params: { [key: string]: any } = { limit: 20 }; // Limit results to 20 for dropdown

        if (debouncedSearchTerm) {
          url = `/data/${entityName}/search`;
          params.q = debouncedSearchTerm;
        }

        const response = await api.get(url, { params });
        setOptions(response.data.map((item: any) => ({
            id: item.id,
            // Attempt to find a display name, prefer 'name', 'title', or first string field in content
            displayName: item.content?.name || item.content?.title ||
                         Object.values(item.content || {}).find(val => typeof val === 'string' && val !== item.id) || // Avoid using ID as display name if possible
                         item.id
        })));
      } catch (err: any) {
        console.error(`Failed to fetch options for ${entityName}:`, err);
        let errorMessage = `Failed to load ${entityName} options.`;
        if (err.response && err.response.data) {
          if (typeof err.response.data === 'string') {
            errorMessage = err.response.data;
          } else if (err.response.data.message) {
            errorMessage = err.response.data.message;
          } else if (err.response.data.detail) {
            if (Array.isArray(err.response.data.detail)) {
              errorMessage = err.response.data.detail.map((e: any) => e.msg || e.message).join('; ');
            } else if (typeof err.response.data.detail === 'string') {
              errorMessage = err.response.data.detail;
            }
          } else if (err.response.data.errors) {
              errorMessage = err.response.data.errors.map((e: any) => e.message || e).join('; ');
          }
        }
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchOptions();
  }, [entityName, debouncedSearchTerm]);

  const handleSelectChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value);
  }, [onChange]);

  return (
    <div className="space-y-1">
      {label && <Label>{label} {required && <span className="text-red-500">*</span>}</Label>}
      {error && <p className="text-red-500 text-sm font-medium border border-red-500 p-2 rounded">{error}</p>}
      <Input
        type="text"
        placeholder={`Search ${entityName}...`}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="mb-2"
        disabled={loading}
      />
      <select
        value={value}
        onChange={handleSelectChange}
        className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
        disabled={loading || !!error} // Disable if loading or error
        required={required}
      >
        <option value="">{placeholder || `Select a ${entityName}`}</option> {/* Not disabled, allows clear selection */}
        {loading && <option value="" disabled>Loading options...</option>}
        {!loading && !error && options.length === 0 && <option value="" disabled>No results found. {entityName && `Create new ${entityName} records first.`}</option>}
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.displayName}
          </option>
        ))}
      </select>
    </div>
  );
}
