/* eslint-disable @typescript-eslint/no-explicit-any */
import { createStore, Store as IStore, AnyAction } from 'redux';
import { Choice } from '../interfaces/choice';
import { Group } from '../interfaces/group';
import { Item } from '../interfaces/item';
import { State } from '../interfaces/state';
import rootReducer from '../reducers/index';

export default class Store {
  _store: IStore;

  constructor() {
    this._store = createStore(
      rootReducer,
      (window as any).__REDUX_DEVTOOLS_EXTENSION__ &&
        (window as any).__REDUX_DEVTOOLS_EXTENSION__(),
    );
  }

  /**
   * Subscribe project to function call (wrapped Redux method)
   */
  subscribe(onChange: () => void): void {
    this._store.subscribe(onChange);
  }

  /**
   * Dispatch event to project (wrapped Redux method)
   */
  dispatch(action: AnyAction): void {
    this._store.dispatch(action);
  }

  /**
   * Get project object (wrapping Redux method)
   */
  get state(): State {
    return this._store.getState();
  }

  /**
   * Get items from project
   */
  get items(): Item[] {
    return this.state.items;
  }

  /**
   * Get active items from project
   */
  get activeItems(): Item[] {
    return this.items.filter((item) => item.active === true);
  }

  /**
   * Get highlighted items from project
   */
  get highlightedActiveItems(): Item[] {
    return this.items.filter((item) => item.active && item.highlighted);
  }

  /**
   * Get choices from project
   */
  get choices(): Choice[] {
    return this.state.choices;
  }

  /**
   * Get active choices from project
   */
  get activeChoices(): Choice[] {
    return this.choices.filter((choice) => choice.active === true);
  }

  /**
   * Get selectable choices from project
   */
  get selectableChoices(): Choice[] {
    return this.choices.filter((choice) => choice.disabled !== true);
  }

  /**
   * Get choices that can be searched (excluding placeholders)
   */
  get searchableChoices(): Choice[] {
    return this.selectableChoices.filter(
      (choice) => choice.placeholder !== true,
    );
  }

  /**
   * Get placeholder choice from project
   */
  get placeholderChoice(): Choice | undefined {
    return [...this.choices]
      .reverse()
      .find((choice) => choice.placeholder === true);
  }

  /**
   * Get groups from project
   */
  get groups(): Group[] {
    return this.state.groups;
  }

  /**
   * Get active groups from project
   */
  get activeGroups(): Group[] {
    const { groups, choices } = this;

    return groups.filter((group) => {
      const isActive = group.active === true && group.disabled === false;
      const hasActiveOptions = choices.some(
        (choice) => choice.active === true && choice.disabled === false,
      );

      return isActive && hasActiveOptions;
    }, []);
  }

  /**
   * Get loading state from project
   */
  isLoading(): boolean {
    return this.state.loading;
  }

  /**
   * Get single choice by it's ID
   */
  getChoiceById(id: string): Choice | undefined {
    return this.activeChoices.find((choice) => choice.id === parseInt(id, 10));
  }

  /**
   * Get group by group id
   */
  getGroupById(id: number): Group | undefined {
    return this.groups.find((group) => group.id === id);
  }
}
