import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-suggested-questions',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './suggested-questions.component.html',
  styleUrls: ['./suggested-questions.component.scss']
})
export class SuggestedQuestionsComponent {
  @Output() public selectQuestion = new EventEmitter<string>();

  public suggestions = [
    'What is ridge regression?',
    'Explain LASSO regression',
    'Compare ridge and LASSO',
    'What is the bias-variance tradeoff?',
    'What is elastic net regression?'
  ];

  public select(q: string): void {
    this.selectQuestion.emit(q);
  }
}
