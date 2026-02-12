import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = '/api';

  constructor(private http: HttpClient) { }

  upload(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.baseUrl}/upload`, formData);
  }

  ask(question: string, documentId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/ask`, {
      question,
      document_id: documentId
    });
  }

  extract(documentId: string, schema: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/extract`, {
      document_id: documentId,
      schema_definition: schema
    });
  }

  proposeSchema(documentId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/propose_schema`, {
      document_id: documentId
    });
  }
}
