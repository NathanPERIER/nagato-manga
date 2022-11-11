import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DownloadPageComponent } from './component/pages/download-page/download-page.component';

const routes: Routes = [
  { path: 'download',  component: DownloadPageComponent, data: {title: null} },
  { path: '**', redirectTo: '/download' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
