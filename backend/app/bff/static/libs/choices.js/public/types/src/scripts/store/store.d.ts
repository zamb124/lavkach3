import { Store as IStore, AnyAction } from 'redux';
import { Choice } from '../interfaces/choice';
import { Group } from '../interfaces/group';
import { Item } from '../interfaces/item';
import { State } from '../interfaces/state';
export default class Store {
    _store: IStore;
    constructor();
    /**
     * Subscribe project to function call (wrapped Redux method)
     */
    subscribe(onChange: () => void): void;
    /**
     * Dispatch event to project (wrapped Redux method)
     */
    dispatch(action: AnyAction): void;
    /**
     * Get project object (wrapping Redux method)
     */
    get state(): State;
    /**
     * Get items from project
     */
    get items(): Item[];
    /**
     * Get active items from project
     */
    get activeItems(): Item[];
    /**
     * Get highlighted items from project
     */
    get highlightedActiveItems(): Item[];
    /**
     * Get choices from project
     */
    get choices(): Choice[];
    /**
     * Get active choices from project
     */
    get activeChoices(): Choice[];
    /**
     * Get selectable choices from project
     */
    get selectableChoices(): Choice[];
    /**
     * Get choices that can be searched (excluding placeholders)
     */
    get searchableChoices(): Choice[];
    /**
     * Get placeholder choice from project
     */
    get placeholderChoice(): Choice | undefined;
    /**
     * Get groups from project
     */
    get groups(): Group[];
    /**
     * Get active groups from project
     */
    get activeGroups(): Group[];
    /**
     * Get loading state from project
     */
    isLoading(): boolean;
    /**
     * Get single choice by it's ID
     */
    getChoiceById(id: string): Choice | undefined;
    /**
     * Get group by group id
     */
    getGroupById(id: number): Group | undefined;
}
//# sourceMappingURL=project.d.ts.map