import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentChunks } from './document-chunks';

describe('DocumentChunks', () => {
  let component: DocumentChunks;
  let fixture: ComponentFixture<DocumentChunks>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DocumentChunks]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DocumentChunks);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
