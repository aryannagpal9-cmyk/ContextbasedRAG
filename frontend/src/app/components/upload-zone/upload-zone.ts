import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';

@Component({
  selector: 'app-upload-zone',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload-zone.html',
  styleUrl: './upload-zone.css',
})
export class UploadZone {
  fileName: string | null = null;
  isDragOver = false;

  constructor(
    private api: ApiService,
    private state: StateService
  ) { }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.handleUpload(file);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave() {
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
    const file = event.dataTransfer?.files[0];
    if (file) {
      this.handleUpload(file);
    }
  }

  private handleUpload(file: File) {
    this.fileName = file.name;
    this.state.setProcessing(true);

    this.api.upload(file).subscribe({
      next: (data) => {
        this.state.setDocument(data);
        this.state.setProcessing(false);
        this.state.addChatMessage({
          text: `Document "${file.name}" processed successfully. You can now chat or extract structured data.`,
          type: 'bot'
        });
      },
      error: (err) => {
        console.error('Upload failed', err);
        this.state.setProcessing(false);
        alert('Upload failed. Please try again.');
      }
    });
  }
}
