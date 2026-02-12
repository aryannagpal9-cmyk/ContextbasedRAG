import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';

interface Message {
  text: string;
  type: 'user' | 'bot';
  intelligence?: any;
  isLoading?: boolean;
}

@Component({
  selector: 'app-chat-interface',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-interface.html',
  styleUrl: './chat-interface.css',
})
export class ChatInterface implements AfterViewChecked {
  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  messages: Message[] = [];
  userInput: string = '';
  documentId: string | null = null;

  constructor(
    private api: ApiService,
    private state: StateService
  ) {
    this.state.documentId$.subscribe(id => this.documentId = id);
    this.state.messages$.subscribe(msgs => this.messages = msgs);
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  sendMessage() {
    const text = this.userInput.trim();
    if (!text || !this.documentId) return;

    this.state.addChatMessage({ text, type: 'user' });
    this.userInput = '';

    const loadingMsg: Message = { text: 'Analyzing document...', type: 'bot', isLoading: true };
    this.state.addChatMessage(loadingMsg);

    this.api.ask(text, this.documentId).subscribe({
      next: (data) => {
        this.replaceLoading(data);
      },
      error: (err) => {
        this.removeLoading();
        this.state.addChatMessage({
          text: 'Sorry, I encountered an error answering that.',
          type: 'bot'
        });
      }
    });
  }

  private replaceLoading(data: any) {
    const msgs = this.state.getCurrentMessages().filter(m => !m.isLoading);
    msgs.push({
      text: data.answer,
      type: 'bot',
      intelligence: data
    });
    this.state.setMessages(msgs);
  }

  private removeLoading() {
    const msgs = this.state.getCurrentMessages().filter(m => !m.isLoading);
    this.state.setMessages(msgs);
  }

  toggleIntelligence(msg: Message) {
    if (msg.intelligence) {
      msg.intelligence.showDetails = !msg.intelligence.showDetails;
    }
  }

  private scrollToBottom(): void {
    try {
      this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    } catch (err) { }
  }

  getMathRound(val: number): number {
    return Math.round(val * 100);
  }
}
