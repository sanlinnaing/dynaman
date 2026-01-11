import React, { useEffect, useState } from 'react';
import { layoutApi, type FormLayout } from '@/lib/api';
import DataInputForm from './DataInputForm';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import api from '@/lib/api';
import { useLanguage } from '@/lib/i18n';

// Match DataInputForm props
interface DynamicFormProps {
  schemaName: string; // Extra prop we need
  schema: any;
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
  recordId?: string;
  initialData?: any;
}

interface LayoutItem {
    id: string;
    type: 'field' | 'structure';
    label: string;
    fieldName?: string;
    fieldType?: string;
    structureType?: string;
    children?: LayoutItem[];
    required?: boolean;
    readOnly?: boolean;
    placeholder?: string;
    helperText?: string;
}

const LayoutRenderer = ({ 
    items, 
    formData, 
    onChange,
    fieldErrors
}: { 
    items: LayoutItem[], 
    formData: any, 
    onChange: (field: string, val: any) => void,
    fieldErrors: Map<string, string>
}) => {
    if (!items) return null;

    return (
        <div className="space-y-4">
            {items.map(item => {
                let errorMessage: string | undefined;
                let isFieldRequiredAndEmpty = false;

                if (item.type === 'field' && item.fieldName) {
                    errorMessage = fieldErrors.get(item.fieldName);
                    
                    if (item.required) {
                        if (item.fieldType === 'boolean') {
                            isFieldRequiredAndEmpty = (formData[item.fieldName] === false || formData[item.fieldName] === undefined);
                        } else {
                            isFieldRequiredAndEmpty = (!formData[item.fieldName] || formData[item.fieldName] === '');
                        }
                        isFieldRequiredAndEmpty = isFieldRequiredAndEmpty && !errorMessage; 
                    }
                    
                    return (
                        <div key={item.id}>
                            <Label htmlFor={item.id}>
                                {item.label}
                                {item.required && <span className="text-red-500 ml-1 font-bold">*</span>}
                            </Label>
                            {item.fieldType === 'boolean' ? (
                                <div className={`flex items-center space-x-2 mt-1 ${isFieldRequiredAndEmpty ? "border border-red-500 rounded p-1" : ""}`}>
                                    <input 
                                        type="checkbox" 
                                        id={item.id}
                                        className="h-4 w-4 rounded border-gray-300"
                                        checked={!!formData[item.fieldName]}
                                        onChange={(e) => onChange(item.fieldName!, e.target.checked)}
                                        disabled={item.readOnly}
                                    />
                                    <span className="text-sm text-muted-foreground">Yes</span>
                                </div>
                            ) : item.fieldType === 'number' ? (
                                <Input 
                                    id={item.id}
                                    type="number"
                                    value={formData[item.fieldName] || ''}
                                    onChange={(e) => onChange(item.fieldName!, Number(e.target.value))}
                                    placeholder={item.placeholder || `Enter ${item.label}`}
                                    disabled={item.readOnly}
                                    className={isFieldRequiredAndEmpty ? "border-red-500" : ""}
                                />
                            ) : item.fieldType === 'date' ? (
                                <Input 
                                    id={item.id}
                                    type="date"
                                    value={formData[item.fieldName] || ''}
                                    onChange={(e) => onChange(item.fieldName!, e.target.value)}
                                    disabled={item.readOnly}
                                    className={isFieldRequiredAndEmpty ? "border-red-500" : ""}
                                />
                            ) : (
                                <Input 
                                    id={item.id}
                                    type="text"
                                    value={formData[item.fieldName] || ''}
                                    onChange={(e) => onChange(item.fieldName!, e.target.value)}
                                    placeholder={item.placeholder || `Enter ${item.label}`}
                                    disabled={item.readOnly}
                                    className={isFieldRequiredAndEmpty ? "border-red-500" : ""}
                                />
                            )}
                            {item.helperText && <p className="text-xs text-muted-foreground mt-1">{item.helperText}</p>}
                            {errorMessage && <p className="text-red-500 text-sm mt-1">{errorMessage}</p>}
                        </div>
                    );
                }
                // Placeholder for structure
                if (item.type === 'structure') {
                    return (
                        <div key={item.id} className="border p-4 rounded bg-gray-50">
                            <h4 className="text-sm font-semibold mb-2">{item.label}</h4>
                            <LayoutRenderer items={item.children || []} formData={formData} onChange={onChange} fieldErrors={fieldErrors} />
                        </div>
                    )
                }
                return null;
            })}
        </div>
    );
};

export const DynamicForm: React.FC<DynamicFormProps> = (props) => {
  const { schemaName, recordId, initialData } = props;
  const [layout, setLayout] = useState<FormLayout | null>(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState<any>({});
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Map<string, string>>(new Map());
  const { t } = useLanguage();

  useEffect(() => {
    if (!props.isOpen) return; 
    
    // Reset form data and errors
    if (initialData) {
        setFormData(initialData);
    } else {
        setFormData({});
    }
    setFieldErrors(new Map());
    setError(null);

    const fetchLayout = async () => {
      setLoading(true);
      const resolvedLayout = await layoutApi.resolve(schemaName);
      setLayout(resolvedLayout);
      setLoading(false);
    };
    fetchLayout();
  }, [schemaName, props.isOpen, initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      setLoading(true);
      setError(null);
      setFieldErrors(new Map()); // Clear field errors on new submit attempt

      try {
        if (recordId) {
            await api.put(`/api/v1/data/${schemaName}/${recordId}`, formData);
        } else {
            await api.post(`/api/v1/data/${schemaName}`, formData);
        }
        props.onSave();
      } catch (err: any) {
          console.error(err);
          if (err.response && err.response.data && Array.isArray(err.response.data.errors)) {
              const newFieldErrors = new Map<string, string>();
              err.response.data.errors.forEach((e: any) => {
                  if (e.field && e.detail) {
                      newFieldErrors.set(e.field, e.detail);
                  }
              });
              setFieldErrors(newFieldErrors);
              setError(err.response.data.message || "Validation failed.");
          } else {
              setError("Failed to save data");
          }
      } finally {
          setLoading(false);
      }
  };

  if (loading && props.isOpen && !layout) {
     return <div>Loading layout...</div>;
  }

  // If we have a custom layout definition, use our custom renderer
  if (layout && layout.definition && layout.definition.length > 0) {
      return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
            <div className="bg-background p-6 rounded-lg shadow-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold">
                        {recordId ? t('form.editTitle', { entity: schemaName }) : t('form.createTitle', { entity: schemaName })}
                    </h2>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">{layout.name}</span>
                </div>

                {error && <div className="text-red-500 mb-4">{error}</div>}

                <form onSubmit={handleSubmit} noValidate>
                    <LayoutRenderer 
                        items={layout.definition} 
                        formData={formData} 
                        onChange={(field, val) => setFormData((prev: any) => ({ ...prev, [field]: val }))} 
                        fieldErrors={fieldErrors}
                    />
                    
                    <div className="flex justify-end space-x-2 mt-6">
                        <Button type="button" variant="outline" onClick={props.onClose}>
                        {t('common.cancel')}
                        </Button>
                        <Button type="submit" disabled={loading}>
                        {loading ? t('form.submitting') : t('form.submit')}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
      );
  }

  // Fallback to default DataInputForm
  return (
    <DataInputForm 
      {...props}
    />
  );
};