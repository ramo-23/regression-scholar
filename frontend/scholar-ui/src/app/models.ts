export interface Source {
  title: string;
  authors?: string;
  section?: string;
  arxiv_url?: string;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}
