import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { CfpFormComponent } from './cfp-form.component';

describe('CfpFormComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CfpFormComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('should initialize form signal with empty values', () => {
    const fixture = TestBed.createComponent(CfpFormComponent);
    const component = fixture.componentInstance;

    expect(component.form()).toEqual({
      name: '',
      email: '',
      talkTitle: '',
      isGDE: false,
    });
  });

  it('should disable submit button when form is invalid', () => {
    const fixture = TestBed.createComponent(CfpFormComponent);
    fixture.detectChanges();

    const button: HTMLButtonElement =
      fixture.nativeElement.querySelector('button[type="submit"]');

    expect(button.disabled).toBe(true);
    expect(fixture.componentInstance.isSubmitDisabled()).toBe(true);
  });
});
