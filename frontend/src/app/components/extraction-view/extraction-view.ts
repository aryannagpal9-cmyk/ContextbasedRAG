import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';

@Component({
  selector: 'app-extraction-view',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './extraction-view.html',
  styleUrl: './extraction-view.css',
})
export class ExtractionView {
  schemaJson: string = '';
  extractionResult: string = '';
  documentId: string | null = null;
  isGeneratingSchema = false;
  isExtracting = false;

  constructor(
    private api: ApiService,
    private state: StateService
  ) {
    this.state.documentId$.subscribe(id => this.documentId = id);
    this.state.proposedSchema$.subscribe(schema => {
      if (schema) this.schemaJson = JSON.stringify(schema, null, 2);
    });
    this.state.extraction$.subscribe(extraction => {
      if (extraction) this.extractionResult = JSON.stringify(extraction, null, 2);
    });
  }

  proposeSchema() {
    if (!this.documentId) return;
    this.isGeneratingSchema = true;
    this.api.proposeSchema(this.documentId).subscribe({
      next: (schema) => {
        this.schemaJson = JSON.stringify(schema, null, 2);
        this.state.setProposedSchema(schema);
        this.isGeneratingSchema = false;
        this.state.addChatMessage({
          text: "I've generated a schema based on the document. You can review and edit it in the Extraction tab.",
          type: 'bot'
        });
      },
      error: (err) => {
        console.error('Schema proposal failed', err);
        this.isGeneratingSchema = false;
        alert('Failed to generate schema.');
      }
    });
  }

  runExtraction() {
    if (!this.documentId || !this.schemaJson) return;

    let schema;
    try {
      schema = JSON.parse(this.schemaJson);
    } catch (e) {
      alert('Invalid JSON schema');
      return;
    }

    this.isExtracting = true;
    this.extractionResult = 'Extracting... This may take a moment.';

    this.api.extract(this.documentId, schema).subscribe({
      next: (data) => {
        this.extractionResult = JSON.stringify(data, null, 2);
        this.state.setExtraction(data);
        this.isExtracting = false;
      },
      error: (err) => {
        console.error('Extraction failed', err);
        this.extractionResult = 'Error during extraction: ' + err.message;
        this.isExtracting = false;
      }
    });
  }
}
