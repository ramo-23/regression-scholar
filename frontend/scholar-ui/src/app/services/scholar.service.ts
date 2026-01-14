import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import type { AskResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class ScholarService {
  private readonly endpoint = 'http://localhost:8000/ask';

  constructor(private readonly http: HttpClient) {}

  public ask(question: string): Observable<AskResponse> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post<AskResponse>(this.endpoint, { question }, { headers });
  }
}
