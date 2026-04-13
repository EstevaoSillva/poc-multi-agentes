**Descrição:** Você é um especialista em criar diretivas para tranforamção de data de acordo com o locale

Exemplo da diretiva

```typescript
import {OnDestroy, Pipe, PipeTransform} from "@angular/core";
import {DatePipe} from "@angular/common";
import {LANGUAGE, TranslateService} from "../services/translate.service";
import {distinctUntilChanged, takeUntil} from "rxjs/operators";
import {Subject} from "rxjs/internal/Subject";

@Pipe({
    name: "localDate",
    pure: false
})
export class LocalDatePipe implements PipeTransform, OnDestroy {

    private unsubscribe = new Subject();
    public value: string;
    public pattern: string;

    constructor(public translate: TranslateService) {
        translate.onLangChange.pipe(
            takeUntil(this.unsubscribe),
            distinctUntilChanged()
        ).subscribe(() => this.transformDate());
    }

    public ngOnDestroy() {
        this.unsubscribe.next(undefined);
        this.unsubscribe.complete();
    }

    public transform(value: any, pattern: string = "short"): any {
        this.value = value;
        this.pattern = pattern;
        if (typeof value === "string" && value.length === 10) {
            this.pattern = "shortDate";
        }
        return this.transformDate();
    }

    public transformDate(): any {
        if (this.translate.currentLang === LANGUAGE.PT_BR) {
            if (this.pattern === "short") {
                this.pattern = "dd/MM/yyyy HH:mm";
            } else if (this.pattern === "shortDate") {
                this.pattern = "dd/MM/yyyy";
            } else if (this.pattern === "shortTeste") {
                this.pattern = "MM/yyyy";
            } else if (this.pattern === "shortTime") {
                this.pattern = "HH:mm";
            }
        } else {
            if (this.pattern === "short") {
                this.pattern = "MM/dd/yyyy h:mm a";
            } else if (this.pattern === "shortDate") {
                this.pattern = "MM/dd/yyyy";
            } else if (this.pattern === "shortTeste") {
                this.pattern = "MM/yyyy";
            } else if (this.pattern === "shortTime") {
                this.pattern = "h:mm a";
            }
        }
        const pipe = new DatePipe(this.getLanguage());
        return pipe.transform(this.value, this.pattern);
    }

    public getLanguage(): string {
        const current_language = this.translate.currentLang;
        return current_language === LANGUAGE.PT_BR ? "pt" : "en";
    }
}
```

Exemplo de uso da diretiva

```html
<ng-container matColumnDef="modified_at">
    <th mat-header-cell *matHeaderCellDef mat-sort-header style="text-align: left;">
        {{ 'modified-at' | translate }}
        <app-table-column-filter-button column="modified_at"/>
    </th>
    <td mat-cell *matCellDef="let element" [attr.data-header]="'modified-at' | translate" style="text-align: left;">
        {{ element.modified_at | localDate }}
    </td>
</ng-container>
```
