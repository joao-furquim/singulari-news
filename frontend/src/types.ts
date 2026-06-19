export interface Category {
  id: string;
  name: string;
  slug: string;
  icon: string | null;
  description: string | null;
}

export interface NewsItem {
  id: string;
  category_id: string;
  title: string;
  source: string;
  summary: string;
  content: string;
  published_at: string;
  created_at: string;
  ai_generated: boolean;
  category?: Category;
}

export interface User {
  id: string;
  name: string;
  email: string;
  locale: string;
  role: 'user' | 'reviewer' | 'admin' | 'root';
  must_change_password: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
  preferences: string[];
}
