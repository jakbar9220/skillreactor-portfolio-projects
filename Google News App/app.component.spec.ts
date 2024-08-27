import "zone.js";
import "zone.js/testing";
import { async, TestBed } from '@angular/core/testing';
import { AppComponent } from './app.component';

describe('AppComponent', () => {
  test(`the title is 'Welcome to SkillReactor!'`, async(() => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app.message).toEqual('Welcome to SkillReactor!');
  }));
});
