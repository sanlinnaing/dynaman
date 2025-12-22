import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import api from '@/lib/api';
import { PlusCircle, Trash2 } from 'lucide-react';
import { Label } from '@/components/ui/label';

interface FieldConstraint {
  unique?: boolean;
}

interface SchemaField {
  name: string;
  field_type: string;
  label: string;
  is_required: boolean;
  reference_target?: string; // New property
  constraints?: FieldConstraint;
}

interface Schema {
  entity_name: string;
  fields: SchemaField[];
}

export default function SchemaEditor() {
  const { entity } = useParams<{ entity: string }>();
  const navigate = useNavigate();
  const [schema, setSchema] = useState<Schema>({ entity_name: '', fields: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableSchemas, setAvailableSchemas] = useState<string[]>([]);

  useEffect(() => {
    const fetchAvailableSchemas = async () => {
      try {
        const response = await api.get('/schemas/');
        setAvailableSchemas(response.data);
      } catch (err) {
        console.error('Failed to fetch available schemas:', err);
      }
    };
    fetchAvailableSchemas();

    if (entity) {
      // Editing existing schema
      const fetchSchema = async () => {
        setLoading(true);
        setError(null);
        try {
          const response = await api.get(`/schemas/${entity}`);
          setSchema(response.data);
        } catch (err) {
          console.error('Failed to fetch schema:', err);
          setError('Failed to load schema.');
        } finally {
          setLoading(false);
        }
      };
      fetchSchema();
    }
  }, [entity]);

  const handleSchemaNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSchema((prev) => ({ ...prev, entity_name: e.target.value }));
  };

  const handleAddField = () => {
    setSchema((prev) => ({
      ...prev,
      fields: [...prev.fields, { name: '', field_type: 'string', label: '', is_required: false }],
    }));
  };

  const handleFieldChange = (
    index: number,
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type, checked } = e.target as HTMLInputElement;
    const newFields = [...schema.fields];
    
    // Handle 'is_reference' checkbox separately
    if (name === 'is_reference') {
        if (checked) {
            newFields[index] = { ...newFields[index], reference_target: availableSchemas.length > 0 ? availableSchemas[0] : undefined, field_type: 'string' };
        } else {
            const { reference_target, ...rest } = newFields[index];
            newFields[index] = { ...rest, field_type: 'string' }; // Revert type to string
        }
    } else if (name === 'is_unique') {
        const currentConstraints = newFields[index].constraints || {};
        newFields[index] = {
            ...newFields[index],
            constraints: {
                ...currentConstraints,
                unique: checked
            }
        };
    } else {
        newFields[index] = {
          ...newFields[index],
          [name]: type === 'checkbox' ? checked : value,
        };
    }

    setSchema((prev) => ({ ...prev, fields: newFields }));
  };

  const handleRemoveField = (index: number) => {
    setSchema((prev) => ({
      ...prev,
      fields: prev.fields.filter((_, i) => i !== index),
    }));
  };

  const validateForm = () => {
    if (!schema.entity_name.trim()) {
      setError('Schema name cannot be empty.');
      return false;
    }
    const fieldNames = new Set<string>();
    for (const field of schema.fields) {
      if (!field.name.trim()) {
        setError('Field name cannot be empty.');
        return false;
      }
      if (fieldNames.has(field.name.trim())) {
        setError(`Duplicate field name: ${field.name}`);
        return false;
      }
      fieldNames.add(field.name.trim());
    }
    setError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      if (entity) {
        // Update existing schema
        await api.put(`/schemas/${entity}`, schema);
      } else {
        // Create new schema
        await api.post('/schemas/', schema);
      }
      navigate('/'); // Navigate to home or dashboard
    } catch (err: any) {
      console.error('Failed to save schema:', err);
      let errorMessage = 'Failed to save schema. Please check your inputs and try again.';
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

  const handleDelete = async () => {
    if (!entity) return;
    if (!window.confirm(`Are you sure you want to delete schema '${entity}'? This action cannot be undone.`)) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await api.delete(`/schemas/${entity}`);
      navigate('/'); // Navigate to home after deletion
    } catch (err: any) {
       console.error('Failed to delete schema:', err);
       setError('Failed to delete schema.');
    } finally {
       setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">
          {entity ? `Edit Schema: ${entity}` : 'Create New Schema'}
        </h1>
        {entity && (
            <Button variant="destructive" onClick={handleDelete} disabled={loading}>
                <Trash2 className="mr-2 h-4 w-4" /> Delete Schema
            </Button>
        )}
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <Label htmlFor="entity_name" className="block text-sm font-medium text-gray-700">Schema Name</Label>
          <Input
            id="entity_name"
            type="text"
            value={schema.entity_name}
            onChange={handleSchemaNameChange}
            disabled={!!entity} // Disable name change for existing schemas
            className="mt-1 block w-full"
            placeholder="e.g., users, products"
          />
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Fields</h2>
          {schema.fields.map((field, index) => (
            <div key={index} className="grid grid-cols-1 md:grid-cols-6 gap-2 items-end border p-4 rounded-md">
              <div className="col-span-2 space-y-1">
                <Label htmlFor={`field-name-${index}`} className="text-sm font-medium text-gray-700">Field Name</Label>
                <Input
                  id={`field-name-${index}`}
                  name="name"
                  type="text"
                  value={field.name}
                  onChange={(e) => handleFieldChange(index, e)}
                  className="w-full"
                  placeholder="e.g., firstName, price"
                />
              </div>
              <div className="col-span-2 space-y-1">
                <Label htmlFor={`field-label-${index}`} className="text-sm font-medium text-gray-700">Label (Optional)</Label>
                <Input
                  id={`field-label-${index}`}
                  name="label"
                  type="text"
                  value={field.label}
                  onChange={(e) => handleFieldChange(index, e)}
                  className="w-full"
                  placeholder="e.g., First Name"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor={`field-type-${index}`} className="text-sm font-medium text-gray-700">Type</Label>
                <select
                  id={`field-type-${index}`}
                  name="field_type"
                  value={field.field_type}
                  onChange={(e) => handleFieldChange(index, e)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={!!field.reference_target} // Disable if it's a reference field
                >
                  <option value="string">String</option>
                  <option value="number">Number</option>
                  <option value="boolean">Boolean</option>
                  <option value="email">Email</option>
                  <option value="date">Date</option>
                  <option value="object">Object</option>
                </select>
              </div>

              {/* Is Reference? checkbox and reference_target select */}
              <div className="col-span-1 space-y-1">
                <div className="flex items-center">
                 <input
                   id={`field-is-reference-${index}`}
                   name="is_reference"
                   type="checkbox"
                   checked={!!field.reference_target}
                   onChange={(e) => handleFieldChange(index, e)}
                   className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
                 />
                 <Label htmlFor={`field-is-reference-${index}`} className="ml-2 text-sm text-gray-700">Is Reference?</Label>
                </div>
                {field.reference_target && (
                  <select
                    id={`field-ref-entity-name-${index}`}
                    name="reference_target"
                    value={field.reference_target}
                    onChange={(e) => handleFieldChange(index, e)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 mt-2"
                  >
                    <option value="">Select Referenced Schema</option>
                    {availableSchemas.map((schemaName) => (
                      <option key={schemaName} value={schemaName}>
                        {schemaName}
                      </option>
                    ))}
                  </select>
                )}
                {/* Required checkbox, moved to below reference_target select for better layout */}
                <div className="flex items-center mt-2">
                 <input
                   id={`field-required-${index}`}
                   name="is_required"
                   type="checkbox"
                   checked={field.is_required}
                   onChange={(e) => handleFieldChange(index, e)}
                   className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
                 />
                 <Label htmlFor={`field-required-${index}`} className="ml-2 text-sm text-gray-700">Required</Label>
                </div>

                {/* Unique Checkbox */}
                <div className="flex items-center mt-2">
                 <input
                   id={`field-unique-${index}`}
                   name="is_unique"
                   type="checkbox"
                   checked={field.constraints?.unique || false}
                   onChange={(e) => handleFieldChange(index, e)}
                   className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
                 />
                 <Label htmlFor={`field-unique-${index}`} className="ml-2 text-sm text-gray-700">Unique</Label>
                </div>
              </div>

              <div className="col-span-1 flex items-center justify-end">
                <Button type="button" variant="ghost" size="icon" onClick={() => handleRemoveField(index)}>
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            </div>
          ))}
          <Button type="button" variant="outline" onClick={handleAddField} className="w-full">
            <PlusCircle className="mr-2 h-4 w-4" /> Add Field
          </Button>
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Saving...' : 'Save Schema'}
        </Button>
      </form>
    </div>
  );
}
