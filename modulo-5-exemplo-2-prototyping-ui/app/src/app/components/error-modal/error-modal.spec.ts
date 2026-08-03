import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ErrorModal } from './error-modal';

describe('ErrorModal', () => {
  let fixture: ComponentFixture<ErrorModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ErrorModal],
    }).compileComponents();

    fixture = TestBed.createComponent(ErrorModal);
    fixture.componentRef.setInput('title', 'Erro de teste');
    fixture.componentRef.setInput('message', 'Mensagem de teste');
    fixture.detectChanges();
  });

  it('should render title and message inputs', () => {
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('.modal-title')?.textContent).toContain('Erro de teste');
    expect(el.querySelector('.modal-message')?.textContent).toContain('Mensagem de teste');
  });

  it('should emit close on button click', () => {
    const closeSpy = vi.fn();
    fixture.componentInstance.close.subscribe(closeSpy);
    (fixture.nativeElement as HTMLElement).querySelector<HTMLButtonElement>('.close-action')?.click();
    expect(closeSpy).toHaveBeenCalled();
  });

  it('should emit close on escape key', () => {
    const closeSpy = vi.fn();
    fixture.componentInstance.close.subscribe(closeSpy);
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    expect(closeSpy).toHaveBeenCalled();
  });
});
