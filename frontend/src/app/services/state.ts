import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class StateService {
  private documentId = new BehaviorSubject<string | null>(null);
  private chunks = new BehaviorSubject<any[]>([]);
  private extraction = new BehaviorSubject<any>(null);
  private proposedSchema = new BehaviorSubject<any>(null);
  private processing = new BehaviorSubject<boolean>(false);
  private messages = new BehaviorSubject<any[]>([]);
  private chunksCount = new BehaviorSubject<number>(0);

  documentId$ = this.documentId.asObservable();
  chunks$ = this.chunks.asObservable();
  chunksCount$ = this.chunksCount.asObservable();
  extraction$ = this.extraction.asObservable();
  proposedSchema$ = this.proposedSchema.asObservable();
  processing$ = this.processing.asObservable();
  messages$ = this.messages.asObservable();

  setDocument(data: any) {
    this.documentId.next(data.document_id);
    this.chunksCount.next(data.chunks_count || 0);
    this.chunks.next(data.chunks || []);
    this.extraction.next(data.extraction || null);
    this.proposedSchema.next(data.proposed_schema || null);
  }

  setProcessing(isProcessing: boolean) {
    this.processing.next(isProcessing);
  }

  setProposedSchema(schema: any) {
    this.proposedSchema.next(schema);
  }

  setExtraction(extraction: any) {
    this.extraction.next(extraction);
  }

  setMessages(msgs: any[]) {
    this.messages.next(msgs);
  }

  addChatMessage(msg: any) {
    const current = this.messages.getValue();
    this.messages.next([...current, msg]);
  }

  getCurrentMessages() {
    return this.messages.getValue();
  }

  getCurrentDocumentId() {
    return this.documentId.getValue();
  }

  getCurrentSchema() {
    return this.proposedSchema.getValue();
  }
}
