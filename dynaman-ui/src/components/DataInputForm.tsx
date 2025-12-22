import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import api from '@/lib/api';
import ReferenceSelect from './ReferenceSelect'; // Import ReferenceSelect

interface SchemaField {
  name: string;
  field_type: string;
  label: string;
  is_required: boolean;
  reference_target?: string; // New property
}

interface Schema {
  entity_name: string;
  fields: SchemaField[];
}

interface DataInputFormProps {
  schema: Schema | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
  recordId?: string;
  initialData?: Record<string, any>;
}

export default function DataInputForm({ schema, isOpen, onClose, onSave, recordId, initialData }: DataInputFormProps) {
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (schema) {
      if (initialData) {
        setFormData(initialData);
      } else {
        const defaultData: Record<string, any> = {};
        schema.fields.forEach(field => {
          // Initialize based on field type or default
          if (field.field_type === 'boolean') defaultData[field.name] = false;
          else if (field.field_type === 'number') defaultData[field.name] = 0;
          else defaultData[field.name] = '';
        });
        setFormData(defaultData);
      }
    }
  }, [schema, isOpen, initialData]); // Reset form when schema changes, form is opened, or initialData changes

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({ ...prev, [fieldName]: value }));
  };

  const validateForm = () => {
    if (!schema) return false;
    for (const field of schema.fields) {
      if (field.is_required) {
        const value = formData[field.name];
        if (value === undefined || value === null || (typeof value === 'string' && value.trim() === '')) {
          setError(`Field '${field.label || field.name}' is required.`);
          return false;
        }
      }
      // Basic type validation (can be more sophisticated)
      if (field.field_type === 'number' && typeof formData[field.name] === 'string' && isNaN(Number(formData[field.name]))) {
        setError(`Field '${field.label || field.name}' must be a number.`);
        return false;
      }
    }
    setError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!schema || !validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      if (recordId) {
        // Edit existing record
        await api.put(`/data/${schema.entity_name}/${recordId}`, formData);
      } else {
        // Create new record
        // The API expects the fields at the root level
        await api.post(`/data/${schema.entity_name}`, formData);
      }
      onSave(); // Notify parent to refresh data
      onClose(); // Close the form
    } catch (err: any) {
      console.error('Failed to save data record:', err);
      let errorMessage = 'Failed to save data. Please check your inputs.';
      if (err.response && err.response.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        } else if (err.response.data.detail) {
          // FastAPI common error format
          if (Array.isArray(err.response.data.detail)) {
            errorMessage = err.response.data.detail.map((e: any) => e.msg || e.message).join('; ');
          } else if (typeof err.response.data.detail === 'string') {
            errorMessage = err.response.data.detail;
          }
        } else if (err.response.data.errors) {
            // General error object with an 'errors' array
            errorMessage = err.response.data.errors.map((e: any) => e.message || e).join('; ');
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !schema) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-background p-6 rounded-lg shadow-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">{recordId ? `Edit Record: ${recordId}` : `Add New Record to ${schema.entity_name}`}</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {schema.fields.map((field) => (
            <div key={field.name}>
              {(typeof field.reference_target === 'string' && field.reference_target.length > 0) ? (
                <ReferenceSelect
                  entityName={field.reference_target}
                  value={formData[field.name] || ''}
                  onChange={(val) => handleFieldChange(field.name, val)}
                  label={field.label || field.name}
                  required={field.is_required}
                />
              ) : (
                <>
                  <Label htmlFor={`input-${field.name}`}>{field.label || field.name} {field.is_required && <span className="text-red-500">*</span>}</Label>
                  {field.field_type === 'string' && (
                    <Input
                      id={`input-${field.name}`}
                      type="text"
                      value={formData[field.name] || ''}
                      onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    />
                  )}
                  {field.field_type === 'email' && (
                    <Input
                      id={`input-${field.name}`}
                      type="email"
                      value={formData[field.name] || ''}
                      onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    />
                  )}
                  {field.field_type === 'number' && (
                    <Input
                      id={`input-${field.name}`}
                      type="number"
                      value={formData[field.name] || 0}
                      onChange={(e) => handleFieldChange(field.name, Number(e.target.value))}
                    />
                  )}
                  {field.field_type === 'boolean' && (
                    <div className="flex items-center space-x-2 mt-1">
                      <input
                        id={`input-${field.name}`}
                        type="checkbox"
                        checked={formData[field.name] || false}
                        onChange={(e) => handleFieldChange(field.name, e.target.checked)}
                        className="h-4 w-4"
                      />
                      <Label htmlFor={`input-${field.name}`} className="sr-only">Checkbox for {field.label || field.name}</Label>
                    </div>
                  )}
                  {field.field_type === 'date' && (
                    <Input
                      id={`input-${field.name}`}
                      type="date"
                      value={formData[field.name] || ''}
                      onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    />
                  )}
                  {field.field_type === 'object' && (
                    <textarea
                      id={`input-${field.name}`}
                      value={formData[field.name] ? JSON.stringify(formData[field.name], null, 2) : ''}
                      onChange={(e) => {
                        try {
                          handleFieldChange(field.name, JSON.parse(e.target.value));
                          setError(null); // Clear error if JSON is valid
                        } catch (jsonErr) {
                          setError(`Invalid JSON for ${field.label || field.name}`);
                        }
                      }}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 mt-1 min-h-[80px]"
                    />
                  )}
                </>
              )}
            </div>
          ))}

          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Add Record'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
