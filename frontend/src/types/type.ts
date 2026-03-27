// src/types/models.ts

export interface Parent {
  id: string;
  parent_name: string;
  email: string;
  created_at: string;
}

export interface Child {
  id: string;
  fullname: string;
  email: string;
  age: number;
  parent_id: string;
  available_balance: number;
  savings_balance: number;
  total_points: number;
  created_at: string;
}

export interface Transaction {
  id: string;
  child_id: string;
  title: string;
  amount: number;
  category: string;
  type: 'income' | 'expense';
  inserted_at: string;
}