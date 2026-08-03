import { ChangeDetectionStrategy, Component, input, output, AfterViewInit, ViewChild, ElementRef, HostListener } from '@angular/core';

@Component({
  selector: 'app-error-modal',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './error-modal.html',
  styleUrl: './error-modal.css',
})
export class ErrorModal implements AfterViewInit {
  readonly title = input.required<string>();
  readonly message = input.required<string>();
  readonly close = output<void>();

  @ViewChild('closeBtn') closeBtn?: ElementRef<HTMLButtonElement>;

  @HostListener('document:keydown.escape')
  onEscape() {
    this.close.emit();
  }

  ngAfterViewInit() {
    this.closeBtn?.nativeElement.focus();
  }
}
