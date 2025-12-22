import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

type Language = 'en' | 'ja';

const translations = {
  en: {
    'app.title': 'Dynaman',
    'nav.platform': 'Platform',
    'nav.dashboard': 'Dashboard',
    'nav.schemaManagement': 'Schema Management',
    'nav.createNew': 'Create New',
    'nav.dataExplorer': 'Data Explorer',
    'nav.noSchemas': 'No schemas found.',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.search': 'Search...',
        'common.refresh': 'Refresh',
        'common.previous': 'Previous',
        'common.next': 'Next',
        'common.page': 'Page {page}',
        'schema.editor.title.create': 'Create New Schema',    'schema.editor.title.edit': 'Edit Schema: {entity}',
    'schema.editor.delete': 'Delete Schema',
    'schema.editor.name': 'Schema Name',
    'schema.editor.fields': 'Fields',
    'schema.editor.fieldName': 'Field Name',
    'schema.editor.label': 'Label (Optional)',
    'schema.editor.type': 'Type',
    'schema.editor.isReference': 'Is Reference?',
    'schema.editor.referenceTarget': 'Select Referenced Schema',
    'schema.editor.required': 'Required',
    'schema.editor.unique': 'Unique',
    'schema.editor.addField': 'Add Field',
    'schema.editor.save': 'Save Schema',
    'schema.editor.saving': 'Saving...',
    'schema.editor.confirmDelete': 'Are you sure you want to delete schema \'{entity}\'? This action cannot be undone.',
    'explorer.title': 'Data Explorer: {entity}',
    'explorer.addData': 'Add Data',
    'explorer.noData': 'No data found.',
    'explorer.actions': 'Actions',
    'explorer.confirmDelete': 'Are you sure you want to delete this record?',
    'explorer.deleteSuccess': 'Record deleted successfully.',
    'explorer.deleteError': 'Failed to delete record.',
    'form.createTitle': 'Create New {entity}',
    'form.editTitle': 'Edit {entity}',
    'form.submit': 'Submit',
    'form.submitting': 'Submitting...', 
    'form.success': 'Record saved successfully.',
    'form.error': 'Failed to save record.',
    'form.validation.required': 'Field \'{label}\' is required.',
    'form.validation.number': 'Field \'{label}\' must be a number.',
    'form.validation.json': 'Invalid JSON for {label}',
    'common.searchEntity': 'Search {entity}...',
    'common.selectEntity': 'Select a {entity}',
    'common.loadingOptions': 'Loading options...',
    'common.noEntityResults': 'No results found. Create new {entity} records first.',
    'common.loadError': 'Failed to load {entity} options.',
    'home.welcome': 'Welcome to Dynaman Admin',
    'home.description': 'Manage your No-Code entities and data records. Select a schema from the sidebar to start exploring data.',
    'home.schemas.title': 'Schemas',
    'home.schemas.description': 'Define and manage your data models dynamically.',
    'home.explorer.title': 'Data Explorer',
    'home.explorer.description': 'View, search, and edit records for any entity.',
    'home.api.title': 'API Ready',
    'home.api.description': 'All data is instantly available via the execution API.',
  },
  ja: {
    'app.title': 'Dynaman',
    'nav.platform': 'プラットフォーム',
    'nav.dashboard': 'ダッシュボード',
    'nav.schemaManagement': 'スキーマ管理',
    'nav.createNew': '新規作成',
    'nav.dataExplorer': 'データエクスプローラー',
    'nav.noSchemas': 'スキーマが見つかりません。',
    'common.save': '保存',
    'common.cancel': 'キャンセル',
    'common.delete': '削除',
    'common.edit': '編集',
        'common.loading': '読み込み中...',
        'common.error': 'エラー',
        'common.search': '検索...',
        'common.refresh': '更新',
        'common.previous': '前へ',
        'common.next': '次へ',
        'common.page': 'ページ {page}',
        'schema.editor.title.create': '新しいスキーマを作成',    'schema.editor.title.edit': 'スキーマ編集: {entity}',
    'schema.editor.delete': 'スキーマを削除',
    'schema.editor.name': 'スキーマ名',
    'schema.editor.fields': 'フィールド',
    'schema.editor.fieldName': 'フィールド名',
    'schema.editor.label': 'ラベル (任意)',
    'schema.editor.type': 'タイプ',
    'schema.editor.isReference': '参照ですか？',
    'schema.editor.referenceTarget': '参照スキーマを選択',
    'schema.editor.required': '必須',
    'schema.editor.unique': 'ユニーク',
    'schema.editor.addField': 'フィールドを追加',
    'schema.editor.save': 'スキーマを保存',
    'schema.editor.saving': '保存中...',
    'schema.editor.confirmDelete': '本当にスキーマ \'{entity}\' を削除してもよろしいですか？この操作は取り消せません。',
    'explorer.title': 'データエクスプローラー: {entity}',
    'explorer.addData': 'データを追加',
    'explorer.noData': 'データが見つかりません。',
    'explorer.actions': 'アクション',
    'explorer.confirmDelete': '本当にこのレコードを削除してもよろしいですか？',
    'explorer.deleteSuccess': 'レコードが正常に削除されました。',
    'explorer.deleteError': 'レコードの削除に失敗しました。',
    'form.createTitle': '{entity} の新規作成',
    'form.editTitle': '{entity} の編集',
    'form.submit': '送信',
    'form.submitting': '送信中...', 
    'form.success': 'レコードが正常に保存されました。',
    'form.error': 'レコードの保存に失敗しました。',
    'form.validation.required': 'フィールド \'{label}\' は必須です。',
    'form.validation.number': 'フィールド \'{label}\' は数値である必要があります。',
    'form.validation.json': '{label} のJSONが無効です',
    'common.searchEntity': '{entity} を検索...',
    'common.selectEntity': '{entity} を選択',
    'common.loadingOptions': 'オプションを読み込み中...',
    'common.noEntityResults': '結果が見つかりません。先に新しい {entity} レコードを作成してください。',
    'common.loadError': '{entity} オプションの読み込みに失敗しました。',
    'home.welcome': 'Dynaman 管理画面へようこそ',
    'home.description': 'No-Code エンティティとデータレコードを管理します。サイドバーからスキーマを選択してデータの探索を開始してください。',
    'home.schemas.title': 'スキーマ',
    'home.schemas.description': 'データモデルを動的に定義および管理します。',
    'home.explorer.title': 'データエクスプローラー',
    'home.explorer.description': '任意のエンティティのレコードを表示、検索、編集します。',
    'home.api.title': 'API 対応',
    'home.api.description': 'すべてのデータは実行 API を介してすぐに利用可能です。',
  }
};

type TranslationKey = keyof typeof translations.en;

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: TranslationKey, params?: Record<string, string>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('en');

  const t = (key: TranslationKey, params?: Record<string, string>) => {
    let text = translations[language][key] || key;
    if (params) {
        Object.entries(params).forEach(([paramKey, paramValue]) => {
            text = text.replace(`{${paramKey}}`, paramValue);
        });
    }
    return text;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
