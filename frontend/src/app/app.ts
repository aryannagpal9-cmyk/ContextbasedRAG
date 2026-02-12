import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { StateService } from './services/state';
import { UploadZone } from './components/upload-zone/upload-zone';
import { ChatInterface } from './components/chat-interface/chat-interface';
import { DocumentChunks } from './components/document-chunks/document-chunks';
import { ExtractionView } from './components/extraction-view/extraction-view';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    UploadZone,
    ChatInterface,
    DocumentChunks,
    ExtractionView
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  activeTab: 'chat' | 'extraction' | 'chunks' = 'chat';
  isProcessing$: Observable<boolean>;
  documentId$: Observable<string | null>;
  chunksCount$: Observable<number>;

  constructor(private state: StateService) {
    this.isProcessing$ = this.state.processing$;
    this.documentId$ = this.state.documentId$;
    this.chunksCount$ = this.state.chunksCount$;
  }

  setActiveTab(tab: 'chat' | 'extraction' | 'chunks') {
    this.activeTab = tab;
  }

  getTruncatedId(id: string | null): string {
    if (!id) return 'None';
    return id.substring(0, 8) + '...';
  }
}
