import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api, { layoutApi, groupApi, type FormLayout, type UserGroup } from '@/lib/api';
import { DndContext, DragOverlay, useDraggable, useDroppable, type DragStartEvent, type DragEndEvent } from '@dnd-kit/core';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, Save, Trash2, Settings } from 'lucide-react';
import { nanoid } from 'nanoid';

interface SchemaField {
  name: string;
  label: string;
  field_type: string;
  is_required: boolean;
}

interface Schema {
  entity_name: string;
  fields: SchemaField[];
}

interface LayoutItem {
    id: string;
    type: 'field' | 'structure';
    label: string;
    // Field props
    fieldName?: string;
    fieldType?: string;
    required?: boolean;
    readOnly?: boolean;
    placeholder?: string;
    helperText?: string;
    // Structure props
    structureType?: string;
    children?: LayoutItem[];
}

// Draggable Toolbox Item Component
function ToolboxItem({ id, label, type, isRequired }: { id: string, label: string, type: string, isRequired: boolean }) {
    const { attributes, listeners, setNodeRef, transform } = useDraggable({
        id: id,
        data: {
            type: 'field',
            label,
            fieldName: id.replace('field-', ''),
            fieldType: type,
            required: isRequired
        }
    });

    const style = transform ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    } : undefined;

    return (
        <div 
            ref={setNodeRef} 
            style={style} 
            {...listeners} 
            {...attributes}
            className="bg-white border p-2 rounded shadow-sm text-sm cursor-grab hover:border-primary touch-none flex justify-between items-center"
        >
            <span>{label} <span className="text-xs text-muted-foreground ml-1">({type})</span></span>
            {isRequired && <span className="text-red-500 text-xs font-bold" title="Required by Schema">*</span>}
        </div>
    );
}

// Draggable Structure Item
function ToolboxStructure({ id, label }: { id: string, label: string }) {
    const { attributes, listeners, setNodeRef, transform } = useDraggable({
        id: id,
        data: {
            type: 'structure',
            label,
            structureType: id.replace('structure-', '')
        }
    });

    const style = transform ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    } : undefined;

    return (
        <div 
            ref={setNodeRef} 
            style={style} 
            {...listeners} 
            {...attributes}
            className="bg-white border p-2 rounded shadow-sm text-sm cursor-grab hover:border-primary touch-none"
        >
            {label}
        </div>
    );
}

// Render Item on Canvas
function CanvasItem({ 
    item, 
    onDelete, 
    onClick, 
    isSelected 
}: { 
    item: LayoutItem, 
    onDelete: (id: string) => void,
    onClick: () => void,
    isSelected: boolean
}) {
    const borderClass = isSelected ? 'border-primary ring-2 ring-primary/20' : 'hover:border-primary';

    if (item.type === 'field') {
        return (
            <div 
                className={`border p-3 rounded mb-2 bg-white flex justify-between items-center group relative cursor-pointer ${borderClass}`}
                onClick={(e) => {
                    e.stopPropagation();
                    onClick();
                }}
            >
                <div className="w-full pointer-events-none">
                    <Label className="font-medium mb-1 block">
                        {item.label}
                        {item.required && <span className="text-red-500 ml-1">*</span>}
                    </Label>
                    {item.fieldType === 'boolean' ? (
                        <div className="flex items-center space-x-2">
                            <input type="checkbox" className="h-4 w-4 rounded border-gray-300" disabled={true} checked={false} readOnly />
                            <span className="text-sm text-muted-foreground">Checkbox</span>
                        </div>
                    ) : item.fieldType === 'number' ? (
                        <Input type="number" placeholder={item.placeholder || "0"} disabled={true} className="bg-gray-50" />
                    ) : item.fieldType === 'date' ? (
                        <Input type="date" disabled={true} className="bg-gray-50" />
                    ) : (
                        <Input type="text" placeholder={item.placeholder || "Text Input"} disabled={true} className="bg-gray-50" />
                    )}
                    {item.helperText && <p className="text-xs text-muted-foreground mt-1">{item.helperText}</p>}
                </div>
                <Button 
                    variant="ghost" 
                    size="icon" 
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-red-500 z-10 pointer-events-auto" 
                    onClick={(e) => { e.stopPropagation(); onDelete(item.id); }}
                >
                    <Trash2 className="h-4 w-4" />
                </Button>
            </div>
        );
    }
    
    if (item.type === 'structure') {
        return (
            <div 
                className={`border border-dashed border-gray-400 p-4 rounded mb-2 bg-gray-50/50 group relative cursor-pointer ${borderClass}`}
                onClick={(e) => {
                    e.stopPropagation();
                    onClick();
                }}
            >
                <div className="text-xs text-muted-foreground uppercase font-semibold mb-2">{item.label}</div>
                <Button variant="ghost" size="icon" className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-red-500" onClick={(e) => { e.stopPropagation(); onDelete(item.id); }}>
                    <Trash2 className="h-4 w-4" />
                </Button>
                <div className="min-h-[50px] bg-white/50 rounded border border-dotted">
                    {/* Nested children would go here */}
                </div>
            </div>
        );
    }
    return null;
}

export default function LayoutDesigner() {
  const { entity } = useParams<{ entity: string }>();
  const [schema, setSchema] = useState<Schema | null>(null);
  const [layouts, setLayouts] = useState<FormLayout[]>([]);
  const [groups, setGroups] = useState<UserGroup[]>([]);
  const [currentLayout, setCurrentLayout] = useState<FormLayout | null>(null);
  const [definition, setDefinition] = useState<LayoutItem[]>([]); // Local state for editor
  const [loading, setLoading] = useState(true);
  const [activeDragId, setActiveDragId] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false); // For settings modal
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);

  // Load Schema, Layouts, and Groups
  useEffect(() => {
    if (!entity) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const [schemaRes, layoutsRes, groupsRes] = await Promise.all([
          api.get(`/api/v1/schemas/${entity}`),
          layoutApi.listBySchema(entity),
          groupApi.list()
        ]);
        setSchema(schemaRes.data);
        setLayouts(layoutsRes);
        setGroups(groupsRes);
        
        if (layoutsRes.length > 0) {
            setCurrentLayout(layoutsRes[0]);
            setDefinition(layoutsRes[0].definition || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [entity]);

  // Sync local definition when layout changes
  useEffect(() => {
      if (currentLayout) {
          setDefinition(currentLayout.definition || []);
          setSelectedItemId(null);
      } else {
          setDefinition([]);
          setSelectedItemId(null);
      }
  }, [currentLayout]);

  const handleCreateLayout = async () => {
      if (!entity) return;
      const name = prompt("Enter layout name (e.g., 'Manager View'):");
      if (!name) return;
      
      try {
          const newLayout = await layoutApi.create({
              schema_name: entity,
              name,
              definition: [], 
              target_group_ids: [],
              is_default: false
          });
          setLayouts([...layouts, newLayout]);
          setCurrentLayout(newLayout);
      } catch (err) {
          alert("Failed to create layout");
      }
  };

  const handleSave = async () => {
      if (!currentLayout) return;

      const definitionToSave = definition.map(item => {
          if (item.type === 'field' && item.fieldName && schema) {
              const correspondingSchemaField = schema.fields.find(f => f.name === item.fieldName);
              if (correspondingSchemaField && correspondingSchemaField.is_required) {
                  return { ...item, required: true }; // Force required true if schema says so
              }
          }
          return item;
      });

      try {
          const updated = await layoutApi.update(currentLayout._id, {
              definition: definitionToSave,
              target_group_ids: currentLayout.target_group_ids,
              is_default: currentLayout.is_default
          });
          // Update local list
          setLayouts(layouts.map(l => l._id === updated._id ? updated : l));
          alert("Layout saved!");
      } catch(err) {
          alert("Failed to save layout");
      }
  };

  const handleDeleteLayout = async () => {
      if (!currentLayout || !confirm("Are you sure you want to delete this layout?")) return;
      try {
          await layoutApi.delete(currentLayout._id);
          const newLayouts = layouts.filter(l => l._id !== currentLayout._id);
          setLayouts(newLayouts);
          setCurrentLayout(newLayouts.length > 0 ? newLayouts[0] : null);
          alert("Layout deleted");
      } catch (err) {
          alert("Failed to delete layout");
      }
  };

  const handleDeleteItem = (id: string) => {
      setDefinition(prev => prev.filter(item => item.id !== id));
      if (selectedItemId === id) setSelectedItemId(null);
  };

  const updateItem = (id: string, updates: Partial<LayoutItem>) => {
      setDefinition(prev => prev.map(item => 
          item.id === id ? { ...item, ...updates } : item
      ));
  };

  const handleDragStart = (event: DragStartEvent) => {
      setActiveDragId(event.active.id as string);
  };

  const handleDragEnd = (event: DragEndEvent) => {
      setActiveDragId(null);
      const { active, over } = event;
      
      if (over && over.id === 'canvas') {
          const data = active.data.current;
          if (!data) return;

          const newItem: LayoutItem = {
              id: nanoid(),
              type: data.type,
              label: data.label,
              fieldName: data.fieldName,
              fieldType: data.fieldType,
              structureType: data.structureType,
              children: [],
              required: data.required // Init from drop
          };

          setDefinition(prev => [...prev, newItem]);
      }
  };

  // Canvas Droppable
  const Canvas = () => {
      const { setNodeRef, isOver } = useDroppable({
          id: 'canvas',
      });
      
      return (
          <div 
            ref={setNodeRef}
            className={`max-w-4xl mx-auto bg-white min-h-[800px] shadow-lg rounded-lg p-8 border ${isOver ? 'border-primary ring-2 ring-primary/20' : 'border-gray-200'}`}
            onClick={() => setSelectedItemId(null)} // Deselect when clicking canvas background
          >
                {!currentLayout ? (
                    <div className="flex items-center justify-center h-full text-muted-foreground">Select or create a layout to start editing</div>
                ) : (
                    <div className="space-y-2">
                        {definition.length === 0 && (
                            <div className="border-2 border-dashed border-gray-300 rounded p-12 text-center text-gray-400">
                                Drop fields here
                            </div>
                        )}
                        {definition.map(item => (
                            <CanvasItem 
                                key={item.id} 
                                item={item} 
                                onDelete={handleDeleteItem}
                                onClick={() => setSelectedItemId(item.id)}
                                isSelected={selectedItemId === item.id}
                            />
                        ))}
                    </div>
                )}
          </div>
      );
  };

  const selectedItem = definition.find(item => item.id === selectedItemId);
  const selectedSchemaField = selectedItem && schema 
    ? schema.fields.find(f => f.name === selectedItem.fieldName) 
    : null;
    
  const isSchemaRequired = selectedSchemaField?.is_required || false;

  if (loading) return <div>Loading designer...</div>;
  if (!schema) return <div>Schema not found</div>;

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="h-14 border-b flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
            <h1 className="font-bold text-lg">Layout Designer: {entity}</h1>
            <select 
                className="border rounded p-1 text-sm"
                value={currentLayout?._id || ''}
                onChange={(e) => setCurrentLayout(layouts.find(l => l._id === e.target.value) || null)}
            >
                {layouts.length === 0 && <option value="">No layouts</option>}
                {layouts.map(l => (
                    <option key={l._id} value={l._id}>{l.name}</option>
                ))}
            </select>
            <Button variant="outline" size="sm" onClick={handleCreateLayout}><Plus className="h-4 w-4 mr-1"/> New Layout</Button>
        </div>
        <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => setShowSettings(true)} disabled={!currentLayout}><Settings className="h-4 w-4 mr-1"/> Settings</Button>
            <Button size="sm" variant="destructive" onClick={handleDeleteLayout} disabled={!currentLayout}><Trash2 className="h-4 w-4 mr-1"/> Delete</Button>
            <Button size="sm" onClick={handleSave} disabled={!currentLayout}><Save className="h-4 w-4 mr-1"/> Save</Button>
        </div>
      </header>

      {/* Settings Modal */}
      {showSettings && currentLayout && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white p-6 rounded-lg shadow-lg w-96">
                  <h2 className="text-lg font-bold mb-4">Layout Settings</h2>
                  
                  <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                          <input 
                              type="checkbox" 
                              id="isDefault" 
                              checked={currentLayout.is_default}
                              onChange={(e) => setCurrentLayout({...currentLayout, is_default: e.target.checked})}
                              className="rounded border-gray-300"
                          />
                          <Label htmlFor="isDefault">Set as Default Layout</Label>
                      </div>

                      <div>
                          <Label className="mb-2 block">Target Groups</Label>
                          <div className="border rounded-md p-2 max-h-40 overflow-y-auto space-y-2">
                            {groups.map(group => (
                              <div key={group._id} className="flex items-center space-x-2">
                                <input 
                                  type="checkbox" 
                                  id={`l-group-${group._id}`}
                                  checked={currentLayout.target_group_ids.includes(group._id)}
                                  onChange={() => {
                                      const ids = currentLayout.target_group_ids;
                                      const newIds = ids.includes(group._id) 
                                        ? ids.filter(i => i !== group._id)
                                        : [...ids, group._id];
                                      setCurrentLayout({...currentLayout, target_group_ids: newIds});
                                  }}
                                  className="rounded border-gray-300"
                                />
                                <Label htmlFor={`l-group-${group._id}`} className="font-normal cursor-pointer flex-1">
                                  {group.name}
                                </Label>
                              </div>
                            ))}
                          </div>
                      </div>
                  </div>

                  <div className="flex justify-end gap-2 mt-6">
                      <Button variant="outline" onClick={() => setShowSettings(false)}>Close</Button>
                  </div>
              </div>
          </div>
      )}

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Toolbox */}
        <aside className="w-64 border-r bg-muted/20 p-4 overflow-y-auto">
            <h3 className="font-semibold mb-4">Fields</h3>
            <div className="space-y-2">
                {schema.fields.map(field => (
                    <ToolboxItem 
                        key={field.name} 
                        id={`field-${field.name}`} 
                        label={field.label || field.name} 
                        type={field.field_type} 
                        isRequired={field.is_required}
                    />
                ))}
            </div>
            
            <h3 className="font-semibold mt-6 mb-4">Structure</h3>
            <div className="space-y-2">
                <ToolboxStructure id="structure-row" label="Row (Columns)" />
                <ToolboxStructure id="structure-section" label="Section Header" />
                <ToolboxStructure id="structure-divider" label="Divider" />
            </div>
        </aside>

        {/* Center: Canvas */}
        <main className="flex-1 bg-gray-100 p-8 overflow-y-auto">
            <Canvas />
        </main>

        {/* Right Sidebar: Properties */}
        <aside className="w-80 border-l bg-white p-4 overflow-y-auto shadow-sm">
            <h3 className="font-semibold mb-4 border-b pb-2">Properties</h3>
            {selectedItem ? (
                <div className="space-y-4">
                    <div>
                        <Label className="mb-1 block">Label</Label>
                        <Input 
                            value={selectedItem.label} 
                            onChange={(e) => updateItem(selectedItem.id, { label: e.target.value })} 
                        />
                    </div>

                    {selectedItem.type === 'field' && (
                        <>
                            <div>
                                <Label className="mb-1 block">Placeholder</Label>
                                <Input 
                                    value={selectedItem.placeholder || ''} 
                                    onChange={(e) => updateItem(selectedItem.id, { placeholder: e.target.value })} 
                                    placeholder="Enter placeholder text..."
                                />
                            </div>

                            <div>
                                <Label className="mb-1 block">Helper Text</Label>
                                <Input 
                                    value={selectedItem.helperText || ''} 
                                    onChange={(e) => updateItem(selectedItem.id, { helperText: e.target.value })} 
                                    placeholder="Explanation for the user..."
                                />
                            </div>

                            <div className="space-y-2 pt-2">
                                <div className="flex items-center space-x-2">
                                    <input 
                                        type="checkbox" 
                                        id="prop-required"
                                        checked={selectedItem.required || isSchemaRequired}
                                        onChange={(e) => {
                                            if (!isSchemaRequired) {
                                                updateItem(selectedItem.id, { required: e.target.checked })
                                            }
                                        }}
                                        disabled={isSchemaRequired}
                                        className="rounded border-gray-300 disabled:opacity-50"
                                    />
                                    <Label htmlFor="prop-required" className="font-normal cursor-pointer">
                                        Required
                                        {isSchemaRequired && <span className="text-xs text-muted-foreground ml-2">(Enforced by Schema)</span>}
                                    </Label>
                                </div>

                                <div className="flex items-center space-x-2">
                                    <input 
                                        type="checkbox" 
                                        id="prop-readonly"
                                        checked={selectedItem.readOnly || false}
                                        onChange={(e) => updateItem(selectedItem.id, { readOnly: e.target.checked })}
                                        className="rounded border-gray-300"
                                    />
                                    <Label htmlFor="prop-readonly" className="font-normal cursor-pointer">Read Only</Label>
                                </div>
                            </div>

                            <div className="text-xs text-muted-foreground mt-4 pt-4 border-t">
                                <p>Field ID: {selectedItem.fieldName}</p>
                                <p>Type: {selectedItem.fieldType}</p>
                            </div>
                        </>
                    )}

                    {selectedItem.type === 'structure' && (
                        <div className="text-sm text-muted-foreground">
                            Structure properties coming soon.
                        </div>
                    )}
                </div>
            ) : (
                <div className="text-sm text-muted-foreground text-center py-8">
                    Select an element on the canvas to edit its properties.
                </div>
            )}
        </aside>
      </div>
      
      <DragOverlay>
          {activeDragId ? (
              <div className="bg-white border p-2 rounded shadow-lg opacity-80 cursor-grabbing">
                  Item
              </div>
          ) : null}
      </DragOverlay>
    </div>
    </DndContext>
  );
}
