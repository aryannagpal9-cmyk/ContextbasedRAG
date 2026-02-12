import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { StateService } from '../../services/state';

@Component({
  selector: 'app-document-chunks',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './document-chunks.html',
  styleUrl: './document-chunks.css',
})
export class DocumentChunks {
  chunks$: Observable<any[]>;

  constructor(private state: StateService) {
    this.chunks$ = this.state.chunks$;
  }

  getSectionType(chunk: any): string {
    return chunk.metadata?.section_type || chunk.section_type || 'misc';
  }

  getPageNumber(chunk: any): string {
    return chunk.metadata?.page_number || chunk.page_number || '?';
  }
}
