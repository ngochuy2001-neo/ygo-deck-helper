"""Service map ORM → schema cho catalog lá bài."""

from __future__ import annotations

from app.models.card import YgoCard, YgoCardImage
from app.repositories.card_repository import CardRepository
from app.schemas.card_catalog import (
    CardDetailResponse,
    CardImageDto,
    CardListItem,
    CardListResponse,
    CardPriceDto,
    CardSetDto,
)
from app.schemas.card_search import CardFilterOptionsResponse, CardSearchParams


def _pick_default_image(images: list[YgoCardImage]) -> YgoCardImage | None:
    if not images:
        return None
    default = next((i for i in images if i.is_default), None)
    return default or images[0]


def _card_to_list_item(card: YgoCard, thumb: str | None) -> CardListItem:
    return CardListItem(
        passcode=card.passcode,
        name=card.name,
        type=card.type,
        atk=card.atk,
        def_=card.def_,
        level=card.level,
        attribute=card.attribute,
        race=card.race,
        image_small_path=thumb,
    )


def _card_to_detail(card: YgoCard) -> CardDetailResponse:
    default_img = _pick_default_image(card.card_images)
    images = [
        CardImageDto(
            image_passcode=img.image_passcode,
            image_path=img.local_path,
            image_small_path=img.local_path_small,
            image_cropped_path=img.local_path_cropped,
            is_default=img.is_default,
        )
        for img in card.card_images
    ]
    prices = None
    if card.card_prices:
        p = card.card_prices
        prices = CardPriceDto(
            cardmarket_price=p.cardmarket_price,
            tcgplayer_price=p.tcgplayer_price,
            ebay_price=p.ebay_price,
            amazon_price=p.amazon_price,
            coolstuffinc_price=p.coolstuffinc_price,
        )

    return CardDetailResponse(
        passcode=card.passcode,
        name=card.name,
        type=card.type,
        frame_type=card.frame_type,
        desc=card.desc,
        atk=card.atk,
        def_=card.def_,
        level=card.level,
        race=card.race,
        attribute=card.attribute,
        scale=card.scale,
        linkval=card.linkval,
        linkmarkers=card.linkmarkers,
        archetype=card.archetype,
        ygoprodeck_url=card.ygoprodeck_url,
        banlist_info=card.banlist_info,
        synced_at=card.synced_at,
        image_path=default_img.local_path if default_img else None,
        image_small_path=default_img.local_path_small if default_img else None,
        images=images,
        card_sets=[
            CardSetDto(
                set_name=s.set_name,
                set_code=s.set_code,
                set_rarity=s.set_rarity,
                set_price=s.set_price,
            )
            for s in card.card_sets
        ],
        prices=prices,
    )


class CardCatalogService:
    def __init__(self, repo: CardRepository) -> None:
        self._repo = repo

    async def search_cards(self, params: CardSearchParams) -> CardListResponse:
        cards, thumbs, total = await self._repo.search_cards(params)
        items = [_card_to_list_item(c, thumbs.get(c.passcode)) for c in cards]
        return CardListResponse(
            items=items,
            total=total,
            offset=params.offset,
            limit=params.limit,
            has_more=params.offset + len(items) < total,
        )

    async def get_filter_options(self) -> CardFilterOptionsResponse:
        data = await self._repo.get_filter_options()
        return CardFilterOptionsResponse(**data)

    async def get_card(self, passcode: int) -> CardDetailResponse | None:
        card = await self._repo.get_card_by_passcode(passcode)
        if card is None:
            return None
        return _card_to_detail(card)
