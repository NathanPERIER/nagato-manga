import { NgModule } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { RouterModule, Routes } from '@angular/router';
import { DownloadPageComponent } from './component/download-page/download-page.component';

const routes: Routes = [
  { path: '',  component: DownloadPageComponent, data: {title: null} },
  { path: '**', redirectTo: '/' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
