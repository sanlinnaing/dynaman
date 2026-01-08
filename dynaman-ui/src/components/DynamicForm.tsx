import React, { useEffect, useState } from 'react';
import { layoutApi, type FormLayout } from '@/lib/api';
import DataInputForm from './DataInputForm';

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

export const DynamicForm: React.FC<DynamicFormProps> = (props) => {
  const { schemaName } = props;
  const [layout, setLayout] = useState<FormLayout | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!props.isOpen) return; // Don't fetch if closed
    
    const fetchLayout = async () => {
      setLoading(true);
      const resolvedLayout = await layoutApi.resolve(schemaName);
      setLayout(resolvedLayout);
      setLoading(false);
    };
    fetchLayout();
  }, [schemaName, props.isOpen]);

  if (loading && props.isOpen) {
     // Render a loading modal placeholder? Or just null?
     // Existing DataInputForm renders a modal. We should probably render a loading state inside a modal structure
     // but for now, let's just let it load.
     return <div>Loading layout...</div>;
  }

  // TODO: In Phase 4, pass 'layout' to DataInputForm or a new renderer.
  // For now, we just pass the props through.
  
  if (layout) {
      console.log("Using Layout:", layout.name);
      // We will eventually pass 'layout={layout}' to DataInputForm
  }

  return (
    <DataInputForm 
      {...props}
    />
  );
};