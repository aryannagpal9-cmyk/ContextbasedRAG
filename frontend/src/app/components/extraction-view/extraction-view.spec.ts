import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExtractionView } from './extraction-view';

describe('ExtractionView', () => {
  let component: ExtractionView;
  let fixture: ComponentFixture<ExtractionView>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ExtractionView]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ExtractionView);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
