import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-download-page',
  templateUrl: './download-page.component.html',
  styleUrls: ['./download-page.component.css']
})
export class DownloadPageComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

  public getRepoLink(): string {
    return environment.repository;
  }

}
